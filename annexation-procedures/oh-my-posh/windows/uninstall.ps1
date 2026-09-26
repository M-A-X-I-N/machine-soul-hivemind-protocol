param([switch]$DryRun)
$ErrorActionPreference = 'Stop'

$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..')) }
$env:MACHINE_SOUL = $root
Import-Module "$root\accumulated-instruments\framework\windows\MachineSoul.psm1" -Force

$hostName = Get-MachineSoulHost
$account = Get-MachineSoulAccount
$state = Join-Path (Get-MachineSoulScratchPath -RelativePath "state\install\$hostName\$account") 'oh-my-posh.json'

if (-not (Test-Path -LiteralPath $state -PathType Leaf)) {
    if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
        'INSTALLED_UNMANAGED'
        exit 1
    }
    'NOT_INSTALLED'
    exit 0
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    'UNSUPPORTED'
    exit 2
}

if ($DryRun) {
    'PLAN: winget uninstall --id JanDeDobbeleer.OhMyPosh --source winget --exact'
    exit 0
}

& winget uninstall --id JanDeDobbeleer.OhMyPosh --source winget --exact --disable-interactivity
if ($LASTEXITCODE -ne 0) { throw "winget uninstall failed with exit code $LASTEXITCODE" }
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    throw 'WinGet reported success, but oh-my-posh remains visible; refusing to erase installation provenance.'
}

Remove-Item -LiteralPath $state -Force
'NOT_INSTALLED'
