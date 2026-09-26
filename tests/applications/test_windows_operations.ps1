$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$env:MACHINE_SOUL = $repoRoot
$env:MACHINE_SOUL_HOST = 'spaceship'
$env:MACHINE_SOUL_ACCOUNT = 'ci-user'

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('machine-soul-apps-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "ASSERTION FAILED: $Message`nexpected: $Expected`nactual:   $Actual"
    }
}

try {
    foreach ($app in @('powershell','windows-terminal','oh-my-posh','contour')) {
        $env:MACHINE_SOUL_CONFIG_DESTINATION = Join-Path $tempRoot "$app\config.file"
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $env:MACHINE_SOUL_CONFIG_DESTINATION) | Out-Null
        $ops = Join-Path $repoRoot "annexation-procedures\$app\windows"

        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app initial check"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'apply_config.ps1') -ConflictPolicy abort) "$app apply"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app check applied"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'apply_config.ps1') -ConflictPolicy abort) "$app idempotent apply"
        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'unapply_config.ps1')) "$app unapply"
        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app final check"
    }

    $env:MACHINE_SOUL_CONFIG_DESTINATION = Join-Path $tempRoot 'cmd\cmdrc.cmd'
    $testRegistryKey = 'HKCU:\Software\MachineSoulTests\' + [Guid]::NewGuid().ToString('N')
    $env:MACHINE_SOUL_CMD_REGISTRY_KEY = $testRegistryKey
    New-Item -ItemType Directory -Force -Path $testRegistryKey | Out-Null
    Set-ItemProperty -LiteralPath $testRegistryKey -Name AutoRun -Value 'echo original' -Type String

    $cmdOps = Join-Path $repoRoot 'annexation-procedures\cmd\windows'
    Assert-Equal 'CONFLICT' (& (Join-Path $cmdOps 'check_config.ps1')) 'cmd initial conflict'
    Assert-Equal 'APPLIED' (& (Join-Path $cmdOps 'apply_config.ps1') -ConflictPolicy 'backup-and-replace') 'cmd apply'
    Assert-Equal 'APPLIED' (& (Join-Path $cmdOps 'check_config.ps1')) 'cmd check applied'
    Assert-Equal 'NOT_APPLIED' (& (Join-Path $cmdOps 'unapply_config.ps1')) 'cmd unapply'
    Assert-Equal 'echo original' ((Get-ItemProperty -LiteralPath $testRegistryKey -Name AutoRun).AutoRun) 'cmd restores prior AutoRun'

    foreach ($app in @('fish','bash','zsh')) {
        $ops = Join-Path $repoRoot "annexation-procedures\$app\windows"
        $output = & (Join-Path $ops 'check_config.ps1')
        Assert-Equal 'NOT_IMPLEMENTED' $output[0] "$app explicit capability gap"
        Assert-Equal 2 $LASTEXITCODE "$app not-implemented exit code"
    }

    $global:LASTEXITCODE = 0
    Write-Host 'Windows application operation tests passed.'
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
