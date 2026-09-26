param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)
$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..')) }
$hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
$account = if ($env:MACHINE_SOUL_ACCOUNT) { $env:MACHINE_SOUL_ACCOUNT } elseif ($env:USERNAME) { $env:USERNAME } else { '' }
$userRel = "assimilation-directives\oh-my-posh\hosts\$hostName\users\$account\theme.omp.json"
$commonRel = "assimilation-directives\oh-my-posh\hosts\$hostName\common\theme.omp.json"
$sourceRel = if (Test-Path -LiteralPath (Join-Path $root $userRel) -PathType Leaf) { $userRel } else { $commonRel }
$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) { $env:MACHINE_SOUL_CONFIG_DESTINATION } else { Join-Path $env:LOCALAPPDATA 'oh-my-posh\theme.omp.json' }
& "$root\accumulated-instruments\configuration-deployment\windows\Invoke-AppConfig.ps1" -Action $Action -Application oh-my-posh -SourceRelative $sourceRel -Destination $destination -ConflictPolicy $ConflictPolicy
