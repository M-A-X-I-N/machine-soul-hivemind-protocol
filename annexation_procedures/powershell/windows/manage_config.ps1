param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$sourceRel = "assimilation_directives\powershell\hosts\$hostName\common\Microsoft.PowerShell_profile.ps1"
$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) { $env:MACHINE_SOUL_CONFIG_DESTINATION } else { $PROFILE.CurrentUserCurrentHost }
& "$root\accumulated_instruments\configuration_deployment\windows\invoke_app_config.ps1" -Action $Action -Application powershell -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
