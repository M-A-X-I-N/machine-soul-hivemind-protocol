$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
Import-Module (Join-Path $repoRoot 'accumulated_instruments\configuration_deployment\windows\MachineSoul.psm1') -Force

$env:MACHINE_SOUL = $repoRoot
$env:MACHINE_SOUL_HOST = 'ci-windows'
$env:MACHINE_SOUL_ACCOUNT = 'ci-user'

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('machine-soul-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "ASSERTION FAILED: $Message`nexpected: $Expected`nactual:   $Actual"
    }
}

try {
    $source = Join-Path $tempRoot 'canonical.conf'
    $destination = Join-Path $tempRoot 'native\config.conf'
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    [System.IO.File]::WriteAllText($source, "canonical`n")

    Assert-Equal 'NOT_APPLIED' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'initial state'

    $result = Invoke-MachineSoulApplyFile -Application 'test-app' -Source $source -Destination $destination -ConflictPolicy abort
    Assert-Equal 'APPLIED' $result.Status 'first apply'
    Assert-Equal $true $result.Changed 'first apply changed'
    Assert-Equal 'APPLIED' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'state after apply'

    $result = Invoke-MachineSoulApplyFile -Application 'test-app' -Source $source -Destination $destination -ConflictPolicy abort
    Assert-Equal 'APPLIED' $result.Status 'idempotent apply'
    Assert-Equal $false $result.Changed 'idempotent apply unchanged'

    $result = Invoke-MachineSoulUnapplyFile -Application 'test-app' -Source $source -Destination $destination
    Assert-Equal 'NOT_APPLIED' $result.Status 'unapply'
    Assert-Equal 'NOT_APPLIED' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'state after unapply'

    [System.IO.File]::WriteAllText($destination, "original`n")
    Assert-Equal 'CONFLICT' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'regular file conflict'

    $result = Invoke-MachineSoulApplyFile -Application 'test-app' -Source $source -Destination $destination -ConflictPolicy abort
    Assert-Equal 'CONFLICT' $result.Status 'abort conflict state'
    Assert-Equal "original`n" ([System.IO.File]::ReadAllText($destination)) 'abort preserves original'

    $result = Invoke-MachineSoulApplyFile -Application 'test-app' -Source $source -Destination $destination -ConflictPolicy 'backup-and-replace'
    Assert-Equal 'APPLIED' $result.Status 'apply over existing file'
    Assert-Equal "canonical`n" ([System.IO.File]::ReadAllText($destination)) 'managed link content'

    $result = Invoke-MachineSoulUnapplyFile -Application 'test-app' -Source $source -Destination $destination
    Assert-Equal 'NOT_APPLIED' $result.Status 'unapply restores original'
    Assert-Equal "original`n" ([System.IO.File]::ReadAllText($destination)) 'original file restored'

    Remove-Item -LiteralPath $destination -Force
    $wrong = Join-Path $tempRoot 'wrong.conf'
    [System.IO.File]::WriteAllText($wrong, "wrong`n")
    New-Item -ItemType SymbolicLink -Path $destination -Target $wrong | Out-Null
    Assert-Equal 'WRONG_TARGET' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'wrong target state'

    Remove-Item -LiteralPath $wrong -Force
    Assert-Equal 'BROKEN' (Get-MachineSoulConfigState -Source $source -Destination $destination) 'broken target state'

    Write-Host 'Windows framework tests passed.'
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\state\config\ci-windows') -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\backups\ci-windows') -Recurse -Force -ErrorAction SilentlyContinue
}
