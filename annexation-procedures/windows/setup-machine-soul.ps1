[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'This setup action is for Windows hosts.'
}

$MachineSoulRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$env:MACHINE_SOUL = $MachineSoulRoot
[Environment]::SetEnvironmentVariable('MACHINE_SOUL', $MachineSoulRoot, 'User')

Write-Host "[Machine Soul] MACHINE_SOUL -> $MachineSoulRoot"
