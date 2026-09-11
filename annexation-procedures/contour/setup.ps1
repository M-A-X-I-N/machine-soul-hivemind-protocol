[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This setup action is for Windows hosts.'
}

$MachineSoulRoot = if ($env:MACHINE_SOUL) {
    $env:MACHINE_SOUL
} else {
    (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

if (-not (Get-Command contour -ErrorAction SilentlyContinue)) {
    Write-Host '[Machine Soul] Contour not found; skipping.'
    return
}

$Source = Join-Path $MachineSoulRoot 'assimilation-directives\contour\contour.yml'
$TargetDirectory = Join-Path $env:LOCALAPPDATA 'contour'
$Target = Join-Path $TargetDirectory 'contour.yml'

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "Canonical Contour config missing: $Source"
}

New-Item -ItemType Directory -Path $TargetDirectory -Force | Out-Null

if (Test-Path -LiteralPath $Target) {
    $Existing = Get-Item -LiteralPath $Target -Force
    if ($Existing.LinkType -eq 'SymbolicLink') {
        try {
            if ((Resolve-Path -LiteralPath $Target).Path -eq (Resolve-Path -LiteralPath $Source).Path) {
                Write-Host '[Machine Soul] Contour config already enabled.'
                return
            }
        } catch {}
    }

    $Backup = "$Target.pre-machine-soul-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $Target -Destination $Backup
    Write-Host "[Machine Soul] Preserved existing Contour config: $Backup"
}

New-Item -ItemType SymbolicLink -Path $Target -Target $Source | Out-Null
Write-Host "[Machine Soul] Contour config -> $Source"
