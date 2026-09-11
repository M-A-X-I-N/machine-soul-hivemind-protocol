[CmdletBinding()]
param(
    [switch]$All,
    [switch]$List,
    [switch]$MachineSoul,
    [string]$Action
)

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This entry point is for Windows hosts. Use ./setup.sh on Linux.'
}

$ActionRoot = Join-Path $PSScriptRoot 'actions'
$MachineSoulSetup = Join-Path $PSScriptRoot 'windows\setup-machine-soul.ps1'

function Get-AvailableActions {
    if (-not (Test-Path -LiteralPath $ActionRoot -PathType Container)) {
        return @()
    }

    @(
        Get-ChildItem -LiteralPath $ActionRoot -Directory |
            ForEach-Object {
                $SetupScript = Join-Path $_.FullName 'setup.ps1'
                if (Test-Path -LiteralPath $SetupScript -PathType Leaf) {
                    [pscustomobject]@{
                        Name   = $_.Name
                        Script = $SetupScript
                    }
                }
            } |
            Sort-Object Name
    )
}

function Invoke-MachineSoulSetup {
    Write-Host "`n[Machine Soul] machine-soul-root"
    & $MachineSoulSetup
}

function Invoke-SetupAction {
    param([Parameter(Mandatory)]$Definition)

    Write-Host "`n[Machine Soul] $($Definition.Name)"
    & $Definition.Script
}

function Invoke-AllSetup {
    Invoke-MachineSoulSetup
    foreach ($Definition in $Actions) {
        Invoke-SetupAction $Definition
    }
}

$Actions = Get-AvailableActions

if ($List) {
    Write-Output 'machine-soul-root'
    $Actions.Name
    return
}

if ($MachineSoul) {
    Invoke-MachineSoulSetup
    return
}

if ($Action) {
    $Match = $Actions | Where-Object Name -IEQ $Action | Select-Object -First 1
    if (-not $Match) {
        throw "No Windows setup action named '$Action' was discovered."
    }

    Invoke-SetupAction $Match
    return
}

if ($All) {
    Invoke-AllSetup
    return
}

while ($true) {
    Write-Host ''
    Write-Host 'Machine Soul Annexation'
    Write-Host '  1. Set up everything available for Windows'
    Write-Host '  2. Establish MACHINE_SOUL repository root'

    for ($Index = 0; $Index -lt $Actions.Count; $Index++) {
        Write-Host ('  {0}. {1}' -f ($Index + 3), $Actions[$Index].Name)
    }

    Write-Host '  Q. Quit'
    $Choice = (Read-Host 'Select action').Trim()

    if ($Choice -ieq 'q') {
        return
    }

    if ($Choice -eq '1') {
        Invoke-AllSetup
        continue
    }

    if ($Choice -eq '2') {
        Invoke-MachineSoulSetup
        continue
    }

    $Selection = 0
    if ([int]::TryParse($Choice, [ref]$Selection)) {
        $ActionIndex = $Selection - 3
        if ($ActionIndex -ge 0 -and $ActionIndex -lt $Actions.Count) {
            Invoke-SetupAction $Actions[$ActionIndex]
            continue
        }
    }

    Write-Warning 'Unknown selection.'
}
