[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "[Machine Soul] $Message"
}

# The script lives in <repo>/annexation-procedures, so its parent is the
# canonical repository root regardless of where the repository is cloned.
$MachineSoulRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

Write-Step "Repository root: $MachineSoulRoot"

# Make the root available immediately to this process and persist it for the
# current Windows user so future shells/applications can resolve the Hivemind.
$env:MACHINE_SOUL = $MachineSoulRoot
[Environment]::SetEnvironmentVariable('MACHINE_SOUL', $MachineSoulRoot, 'User')
Write-Step 'Established user environment variable MACHINE_SOUL.'

# Contour is optional. If it is installed, bind its canonical Windows config
# path to the configuration stored in the repository.
$Contour = Get-Command contour -ErrorAction SilentlyContinue
if (-not $Contour) {
    Write-Step 'Contour not found; skipping Contour assimilation.'
    return
}

$ContourSource = Join-Path $MachineSoulRoot 'assimilation-directives\contour\contour.yml'
$ContourConfigDirectory = Join-Path $env:LOCALAPPDATA 'contour'
$ContourConfigPath = Join-Path $ContourConfigDirectory 'contour.yml'

if (-not (Test-Path -LiteralPath $ContourSource -PathType Leaf)) {
    throw "Canonical Contour configuration is missing: $ContourSource"
}

New-Item -ItemType Directory -Path $ContourConfigDirectory -Force | Out-Null

if (Test-Path -LiteralPath $ContourConfigPath) {
    $Existing = Get-Item -LiteralPath $ContourConfigPath -Force

    if ($Existing.LinkType -eq 'SymbolicLink') {
        $ResolvedTarget = $null
        try {
            $ResolvedTarget = (Resolve-Path -LiteralPath $ContourConfigPath).Path
        }
        catch {
            # Broken/wrong symlink: replace it below after preserving its path.
        }

        if ($ResolvedTarget -eq (Resolve-Path -LiteralPath $ContourSource).Path) {
            Write-Step 'Contour configuration is already linked to the Machine Soul.'
            return
        }
    }

    $Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $BackupPath = "$ContourConfigPath.pre-machine-soul-$Timestamp"
    Move-Item -LiteralPath $ContourConfigPath -Destination $BackupPath
    Write-Step "Preserved existing Contour configuration as: $BackupPath"
}

try {
    New-Item -ItemType SymbolicLink -Path $ContourConfigPath -Target $ContourSource | Out-Null
}
catch {
    throw @"
Failed to create the Contour configuration symlink.

Source: $ContourSource
Target: $ContourConfigPath

On Windows, creating symbolic links may require Developer Mode or an elevated shell.
Original error: $($_.Exception.Message)
"@
}

Write-Step "Linked Contour configuration: $ContourConfigPath -> $ContourSource"
