param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$sourceRel = "assimilation_directives\contour\hosts\$hostName\common\contour.yml"
$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) { $env:MACHINE_SOUL_CONFIG_DESTINATION } else { Join-Path $env:LOCALAPPDATA 'contour\contour.yml' }
& "$root\accumulated_instruments\configuration_deployment\windows\invoke_app_config.ps1" -Action $Action -Application contour -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
