[CmdletBinding()]
param(
    [switch]$All,
    [ValidateSet('machine-soul-root', 'contour')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This entry point is for Windows hosts. Use ./setup.sh on Linux.'
}

$Actions = [ordered]@{
    'machine-soul-root' = @{
        Label  = 'Establish MACHINE_SOUL repository root'
        Script = Join-Path $PSScriptRoot 'machine-soul-root\setup.ps1'
    }
    'contour' = @{
        Label  = 'Enable Contour configuration'
        Script = Join-Path $PSScriptRoot 'contour\setup.ps1'
    }
}

function Invoke-SetupAction {
    param([Parameter(Mandatory)][string]$Name)

    $Definition = $Actions[$Name]
    if (-not $Definition) {
        throw "Unknown setup action: $Name"
    }

    Write-Host "`n[Machine Soul] $($Definition.Label)"
    & $Definition.Script
}

function Invoke-AllSetupActions {
    foreach ($Name in $Actions.Keys) {
        Invoke-SetupAction -Name $Name
    }
}

if ($All) {
    Invoke-AllSetupActions
    return
}

if ($Action) {
    Invoke-SetupAction -Name $Action
    return
}

while ($true) {
    Write-Host ''
    Write-Host 'Machine Soul Annexation'
    Write-Host '  1. Set up everything for current OS'
    Write-Host '  2. Establish MACHINE_SOUL repository root'
    Write-Host '  3. Enable Contour configuration'
    Write-Host '  Q. Quit'

    switch ((Read-Host 'Select action').Trim().ToLowerInvariant()) {
        '1' { Invoke-AllSetupActions }
        '2' { Invoke-SetupAction -Name 'machine-soul-root' }
        '3' { Invoke-SetupAction -Name 'contour' }
        'q' { return }
        default { Write-Warning 'Unknown selection.' }
    }
}
