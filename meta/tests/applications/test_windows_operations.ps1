$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$env:MACHINE_SOUL = $repoRoot
$env:MACHINE_SOUL_HOST = 'spaceship'
Remove-Item Env:MACHINE_SOUL_ACCOUNT -ErrorAction SilentlyContinue

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('machine-soul-apps-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

function Invoke-Wrapper {
    param(
        [Parameter(Mandatory)][string]$Path,
        [string[]]$Arguments = @()
    )
    $raw = & python $Path --json @Arguments
    return ($raw | ConvertFrom-Json)
}

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "ASSERTION FAILED: $Message`nexpected: $Expected`nactual:   $Actual"
    }
}

try {
    foreach ($app in @('powershell','windows_terminal','oh_my_posh','contour')) {
        $env:MACHINE_SOUL_CONFIG_DESTINATION = Join-Path $tempRoot "$app\config.file"
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $env:MACHINE_SOUL_CONFIG_DESTINATION) | Out-Null
        $ops = Join-Path $repoRoot "annexation_procedures\$app"

        Assert-Equal 'not_applied' (Invoke-Wrapper (Join-Path $ops 'check_config.py')).code "$app initial check"
        Assert-Equal 'applied' (Invoke-Wrapper (Join-Path $ops 'apply_config.py') @('--conflict-policy','abort')).code "$app apply"
        Assert-Equal 'applied' (Invoke-Wrapper (Join-Path $ops 'check_config.py')).code "$app check applied"
        Assert-Equal 'applied' (Invoke-Wrapper (Join-Path $ops 'apply_config.py') @('--conflict-policy','abort')).code "$app idempotent apply"
        Assert-Equal 'not_applied' (Invoke-Wrapper (Join-Path $ops 'unapply_config.py')).code "$app unapply"
        Assert-Equal 'not_applied' (Invoke-Wrapper (Join-Path $ops 'check_config.py')).code "$app final check"
    }

    $env:MACHINE_SOUL_CONFIG_DESTINATION = Join-Path $tempRoot 'cmd\cmdrc.cmd'
    $testRegistryKey = 'HKCU:\Software\MachineSoulTests\' + [Guid]::NewGuid().ToString('N')
    $env:MACHINE_SOUL_CMD_REGISTRY_KEY = $testRegistryKey
    New-Item -ItemType Directory -Force -Path $testRegistryKey | Out-Null
    Set-ItemProperty -LiteralPath $testRegistryKey -Name AutoRun -Value 'echo original' -Type String

    $cmdOps = Join-Path $repoRoot 'annexation_procedures\cmd'
    Assert-Equal 'conflict' (Invoke-Wrapper (Join-Path $cmdOps 'check_config.py')).code 'cmd initial conflict'
    Assert-Equal 'applied' (Invoke-Wrapper (Join-Path $cmdOps 'apply_config.py') @('--conflict-policy','backup_and_replace')).code 'cmd apply'
    Assert-Equal 'applied' (Invoke-Wrapper (Join-Path $cmdOps 'check_config.py')).code 'cmd check applied'
    Assert-Equal 'not_applied' (Invoke-Wrapper (Join-Path $cmdOps 'unapply_config.py')).code 'cmd unapply'
    Assert-Equal 'echo original' ((Get-ItemProperty -LiteralPath $testRegistryKey -Name AutoRun).AutoRun) 'cmd restores prior AutoRun'

    $global:LASTEXITCODE = 0
    Write-Host 'Windows Python-wrapper application operation tests passed.'
}
finally {
    if ($env:MACHINE_SOUL_CMD_REGISTRY_KEY) {
        Remove-Item -LiteralPath $env:MACHINE_SOUL_CMD_REGISTRY_KEY -Recurse -Force -ErrorAction SilentlyContinue
    }
    Remove-Item Env:MACHINE_SOUL_CMD_REGISTRY_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:MACHINE_SOUL_CONFIG_DESTINATION -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\state\config\spaceship') -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\backups\spaceship') -Recurse -Force -ErrorAction SilentlyContinue
}
