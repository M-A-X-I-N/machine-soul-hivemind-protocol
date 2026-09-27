param([switch]$DryRun)
$ErrorActionPreference = 'Stop'

$root = if ($env:MACHINE_SOUL) { $env:MACHINE_SOUL } else { [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..')) }
$env:MACHINE_SOUL = $root
Import-Module "$root\accumulated_instruments\configuration_deployment\windows\MachineSoul.psm1" -Force

$hostName = Get-MachineSoulHost
$account = Get-MachineSoulAccount
$stateDir = Get-MachineSoulScratchPath -RelativePath "state\install\$hostName\$account" -CreateDirectory
$state = Join-Path $stateDir 'oh_my_posh.json'

if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    if (Test-Path -LiteralPath $state -PathType Leaf) { 'INSTALLED_MANAGED' } else { 'INSTALLED_UNMANAGED' }
    exit 0
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    'UNSUPPORTED'
    exit 2
}

if ($DryRun) {
    'PLAN: winget install --id JanDeDobbeleer.OhMyPosh --source winget --exact'
    exit 0
}

& winget install --id JanDeDobbeleer.OhMyPosh --source winget --exact --accept-package-agreements --accept-source-agreements --disable-interactivity
if ($LASTEXITCODE -ne 0) { throw "winget install failed with exit code $LASTEXITCODE" }
if (-not (Get-Command oh-my-posh -ErrorAction SilentlyContinue)) {
    throw 'WinGet reported success, but oh-my-posh is not visible in the current command path.'
}

@{
    schema = 1
    application = 'oh_my_posh'
    manager = 'winget'
    package_id = 'JanDeDobbeleer.OhMyPosh'
    source = 'winget'
    host = $hostName
    account = $account
} | ConvertTo-Json | Set-Content -LiteralPath $state -Encoding UTF8

'INSTALLED_MANAGED'
