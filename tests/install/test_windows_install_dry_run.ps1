$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$env:MACHINE_SOUL = $repoRoot
$env:MACHINE_SOUL_HOST = 'ci-install-windows'
$env:MACHINE_SOUL_ACCOUNT = 'ci-user'

$state = Join-Path $repoRoot 'scratch\state\install\ci-install-windows\ci-user\oh_my_posh.json'
try {
    $script = Join-Path $repoRoot 'annexation_procedures\oh_my_posh\windows\install.ps1'
    $output = & $script -DryRun

    if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
        if ($output -ne 'INSTALLED_UNMANAGED') {
            throw "Expected unmanaged OMP on preinstalled runner, got: $output"
        }
    } else {
        if ($output -notlike 'PLAN:*') {
            throw "Unexpected OMP dry-run output: $output"
        }
    }

    if (Test-Path -LiteralPath $state -PathType Leaf) {
        throw 'Dry-run or unmanaged detection must not claim OMP installation ownership.'
    }

    $global:LASTEXITCODE = 0
    Write-Host 'Windows installation dry-run/provenance test passed.'
}
finally {
    Remove-Item -LiteralPath (Join-Path $repoRoot 'scratch\state\install\ci-install-windows') -Recurse -Force -ErrorAction SilentlyContinue
}
