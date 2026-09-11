[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Target
)

$ErrorActionPreference = 'Stop'

$SourcePath = (Resolve-Path -LiteralPath $Source).Path
$TargetDirectory = Split-Path -Parent $Target

if ($TargetDirectory) {
    New-Item -ItemType Directory -Path $TargetDirectory -Force | Out-Null
}

if (Test-Path -LiteralPath $Target) {
    $Existing = Get-Item -LiteralPath $Target -Force

    if ($Existing.LinkType -eq 'SymbolicLink') {
        try {
            if ((Resolve-Path -LiteralPath $Target).Path -eq $SourcePath) {
                Write-Host "[Machine Soul] Symlink already correct: $Target -> $SourcePath"
                return
            }
        }
        catch {
            # Broken symlink; preserve and replace it below.
        }
    }

    $Backup = "$Target.pre-machine-soul-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $Target -Destination $Backup
    Write-Host "[Machine Soul] Preserved existing target: $Backup"
}

New-Item -ItemType SymbolicLink -Path $Target -Target $SourcePath | Out-Null
Write-Host "[Machine Soul] Linked: $Target -> $SourcePath"
