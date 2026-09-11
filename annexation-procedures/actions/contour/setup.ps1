[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This setup action is for Windows hosts.'
}

if (-not (Get-Command contour -ErrorAction SilentlyContinue)) {
    Write-Host '[Machine Soul] Contour not found; skipping.'
    return
}

$MachineSoulRoot = if ($env:MACHINE_SOUL) {
    $env:MACHINE_SOUL
} else {
    (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

$Source = Join-Path $MachineSoulRoot 'assimilation-directives\contour\contour.yml'
$Target = Join-Path $env:LOCALAPPDATA 'contour\contour.yml'
$SymlinkHelper = Join-Path $MachineSoulRoot 'annexation-procedures\windows\make-symlink.ps1'

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "Canonical Contour config missing: $Source"
}

& $SymlinkHelper -Source $Source -Target $Target
