[CmdletBinding()]
param(
    [switch]$All,
    [switch]$List,
    [string]$Action
)

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This entry point is for Windows hosts. Use ./setup.sh on Linux.'
}

$ActionRoot = Join-Path $PSScriptRoot 'actions'

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

function Invoke-SetupAction {
    param([Parameter(Mandatory)]$Definition)

    Write-Host "`n[Machine Soul] $($Definition.Name)"
    & $Definition.Script
}

$Actions = Get-AvailableActions

if ($List) {
    $Actions.Name
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
    foreach ($Definition in $Actions) {
        Invoke-SetupAction $Definition
    }
    return
}

if ($Actions.Count -eq 0) {
    Write-Host '[Machine Soul] No Windows setup actions were discovered.'
    return
}

while ($true) {
    Write-Host ''
    Write-Host 'Machine Soul Annexation'
    Write-Host '  1. Set up everything available for Windows'

    for ($Index = 0; $Index -lt $Actions.Count; $Index++) {
        Write-Host ('  {0}. {1}' -f ($Index + 2), $Actions[$Index].Name)
    }

    Write-Host '  Q. Quit'
    $Choice = (Read-Host 'Select action').Trim()

    if ($Choice -ieq 'q') {
        return
    }

    if ($Choice -eq '1') {
        foreach ($Definition in $Actions) {
            Invoke-SetupAction $Definition
        }
        continue
    }

    $Selection = 0
    if ([int]::TryParse($Choice, [ref]$Selection)) {
        $ActionIndex = $Selection - 2
        if ($ActionIndex -ge 0 -and $ActionIndex -lt $Actions.Count) {
            Invoke-SetupAction $Actions[$ActionIndex]
            continue
        }
    }

    Write-Warning 'Unknown selection.'
}
