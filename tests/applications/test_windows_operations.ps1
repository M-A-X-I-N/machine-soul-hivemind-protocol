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
        $ops = Join-Path $repoRoot "assimilation-directives\$app\operations\windows"

        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app initial check"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'apply_config.ps1') -ConflictPolicy abort) "$app apply"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app check applied"
        Assert-Equal 'APPLIED' (& (Join-Path $ops 'apply_config.ps1') -ConflictPolicy abort) "$app idempotent apply"
        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'unapply_config.ps1')) "$app unapply"
        Assert-Equal 'NOT_APPLIED' (& (Join-Path $ops 'check_config.ps1')) "$app final check"
    }

    foreach ($app in @('fish','bash','zsh','cmd')) {
        $ops = Join-Path $repoRoot "assimilation-directives\$app\operations\windows"
        $output = & (Join-Path $ops 'check_config.ps1')
        Assert-Equal 'NOT_IMPLEMENTED' $output[0] "$app explicit capability gap"
        Assert-Equal 2 $LASTEXITCODE "$app not-implemented exit code"
    }

    $global:LASTEXITCODE = 0
    Write-Host 'Windows application operation tests passed.'
}
finally {
    Remove-Item Env:MACHINE_SOUL_CONFIG_DESTINATION -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\state\config\spaceship') -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\backups\spaceship') -Recurse -Force -ErrorAction SilentlyContinue
}
