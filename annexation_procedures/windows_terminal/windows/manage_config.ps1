param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$sourceRel = "assimilation_directives\windows_terminal\hosts\$hostName\common\settings.json"
$packaged = Join-Path $env:LOCALAPPDATA 'Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json'
$unpackaged = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows Terminal\settings.json'
$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) { $env:MACHINE_SOUL_CONFIG_DESTINATION } else { if (Test-Path -LiteralPath (Split-Path -Parent $packaged) -PathType Container) { $packaged } else { $unpackaged } }
& "$root\accumulated_instruments\configuration_deployment\windows\Invoke-AppConfig.ps1" -Action $Action -Application windows_terminal -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
