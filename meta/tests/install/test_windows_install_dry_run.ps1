$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$env:MACHINE_SOUL = $repoRoot
$env:MACHINE_SOUL_HOST = 'ci_install_windows'
Remove-Item Env:MACHINE_SOUL_ACCOUNT -ErrorAction SilentlyContinue

try {
    $script = Join-Path $repoRoot 'annexation\oh_my_posh\install.py'
    $raw = & python $script --dry-run --json
    $result = $raw | ConvertFrom-Json

    if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
        if ($result.code -ne 'installed_unmanaged') {
            throw "Expected unmanaged OMP on preinstalled runner, got: $($result.code)"
        }
    } else {
        if ($result.code -ne 'would_install') {
            throw "Unexpected OMP dry-run result: $($result.code)"
        }
    }

    $stateRoot = Join-Path $repoRoot 'scratch\state\install\ci_install_windows'
    if (Test-Path -LiteralPath $stateRoot -PathType Container) {
        $owned = Get-ChildItem -LiteralPath $stateRoot -File -Recurse -ErrorAction SilentlyContinue
        if ($owned) {
            throw 'Dry-run or unmanaged detection must not claim OMP installation ownership.'
        }
    }

    $global:LASTEXITCODE = 0
    Write-Host 'Windows Python installation dry-run/provenance test passed.'
}
finally {
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\state\install\ci_install_windows') -Recurse -Force -ErrorAction SilentlyContinue
}
