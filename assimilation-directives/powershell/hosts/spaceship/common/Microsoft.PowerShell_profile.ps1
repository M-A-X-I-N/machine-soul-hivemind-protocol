# Machine-Soul PowerShell profile.

if ($env:MACHINE_SOUL -and (Get-Command oh-my-posh -ErrorAction SilentlyContinue)) {
    $hostName = if ($env:MACHINE_SOUL_HOST) { $env:MACHINE_SOUL_HOST.ToLowerInvariant() } elseif ($env:COMPUTERNAME) { $env:COMPUTERNAME.ToLowerInvariant() } else { 'spaceship' }
    $userName = if ($env:MACHINE_SOUL_ACCOUNT) { $env:MACHINE_SOUL_ACCOUNT } elseif ($env:USERNAME) { $env:USERNAME } else { '' }
    $userConfig = Join-Path $env:MACHINE_SOUL "assimilation-directives\oh-my-posh\config\hosts\$hostName\users\$userName\theme.omp.json"
    $commonConfig = Join-Path $env:MACHINE_SOUL "assimilation-directives\oh-my-posh\config\hosts\$hostName\common\theme.omp.json"
    if (Test-Path -LiteralPath $userConfig -PathType Leaf) {
        oh-my-posh init pwsh --config $userConfig | Invoke-Expression
    } elseif (Test-Path -LiteralPath $commonConfig -PathType Leaf) {
        oh-my-posh init pwsh --config $commonConfig | Invoke-Expression
    }
}
