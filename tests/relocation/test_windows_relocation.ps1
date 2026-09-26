$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$actualRepo = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
Import-Module (Join-Path $actualRepo 'accumulated-instruments\framework\windows\MachineSoul.psm1') -Force

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('machine-soul-relocate-' + [Guid]::NewGuid().ToString('N'))
$oldRoot = Join-Path $tmp 'old-soul'
$newRoot = Join-Path $tmp 'new-soul'
$destination = Join-Path $tmp 'native\config.file'

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "ASSERTION FAILED: $Message`nexpected: $Expected`nactual:   $Actual"
    }
}

try {
    New-Item -ItemType Directory -Force -Path (Join-Path $oldRoot 'config') | Out-Null
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $oldRoot 'TASKS.md'), "# marker`n")
    [System.IO.File]::WriteAllText((Join-Path $oldRoot 'config\canonical.conf'), "canonical`n")
    [System.IO.File]::WriteAllText($destination, "original`n")

    $env:MACHINE_SOUL = $oldRoot
    $env:MACHINE_SOUL_HOST = 'relocation-windows'
    $env:MACHINE_SOUL_ACCOUNT = 'tester'

    $result = Invoke-MachineSoulApplyFile -Application 'relocation-test' -Source (Join-Path $oldRoot 'config\canonical.conf') -Destination $destination -ConflictPolicy 'backup-and-replace'
    Assert-Equal 'APPLIED' $result.Status 'initial apply'

    Move-Item -LiteralPath $oldRoot -Destination $newRoot
    $env:MACHINE_SOUL = $newRoot
    $newSource = Join-Path $newRoot 'config\canonical.conf'

    $state = Get-MachineSoulConfigState -Source $newSource -Destination $destination
    if ($state -ne 'BROKEN' -and $state -ne 'WRONG_TARGET') {
        throw "Expected stale link after relocation, got: $state"
    }

    $result = Invoke-MachineSoulApplyFile -Application 'relocation-test' -Source $newSource -Destination $destination -ConflictPolicy abort
    Assert-Equal 'APPLIED' $result.Status 'repair relocated link'
    Assert-Equal 'APPLIED' (Get-MachineSoulConfigState -Source $newSource -Destination $destination) 'state after repair'
    Assert-Equal "canonical`n" ([System.IO.File]::ReadAllText($destination)) 'canonical content after repair'

    $result = Invoke-MachineSoulUnapplyFile -Application 'relocation-test' -Source $newSource -Destination $destination
    Assert-Equal 'NOT_APPLIED' $result.Status 'unapply after relocation'
    Assert-Equal "original`n" ([System.IO.File]::ReadAllText($destination)) 'original restored after relocation'

    $global:LASTEXITCODE = 0
    Write-Host 'Windows relocation/restore-lineage test passed.'
}
finally {
    Remove-Item Env:MACHINE_SOUL -ErrorAction SilentlyContinue
    Remove-Item Env:MACHINE_SOUL_HOST -ErrorAction SilentlyContinue
    Remove-Item Env:MACHINE_SOUL_ACCOUNT -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
