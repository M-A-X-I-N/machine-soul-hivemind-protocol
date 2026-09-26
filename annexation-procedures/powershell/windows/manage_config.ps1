param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$sourceRel = "assimilation-directives\powershell\config\hosts\$hostName\common\Microsoft.PowerShell_profile.ps1"
$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) { $env:MACHINE_SOUL_CONFIG_DESTINATION } else { $PROFILE.CurrentUserCurrentHost }
& "$root\accumulated-instruments\framework\windows\Invoke-AppConfig.ps1" -Action $Action -Application powershell -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
