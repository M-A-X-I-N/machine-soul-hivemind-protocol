param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$sourceRel = "assimilation-directives\windows-terminal\config\hosts\$hostName\common\settings.json"
$packaged = Join-Path $env:LOCALAPPDATA 'Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json'
$unpackaged = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows Terminal\settings.json'
$destination = if (Test-Path -LiteralPath (Split-Path -Parent $packaged) -PathType Container) { $packaged } else { $unpackaged }
& "$root\accumulated-instruments\framework\windows\Invoke-AppConfig.ps1" -Action $Action -Application windows-terminal -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
