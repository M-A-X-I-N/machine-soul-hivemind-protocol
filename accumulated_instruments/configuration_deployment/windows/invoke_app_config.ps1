param(
    [Parameter(Mandatory)][ValidateSet('check','apply','unapply')][string]$Action,
    [Parameter(Mandatory)][string]$Application,
    [Parameter(Mandatory)][string]$SourceRelative,
    [Parameter(Mandatory)][string]$Destination,
    [ValidateSet('prompt','abort','backup-and-replace')][string]$ConflictPolicy = 'prompt'
)

$ErrorActionPreference = 'Stop'
$modulePath = Join-Path $PSScriptRoot 'MachineSoul.psm1'
Import-Module $modulePath -Force
$root = Get-MachineSoulRoot
$source = Join-Path $root $SourceRelative

switch ($Action) {
    'check' {
        Get-MachineSoulConfigState -Source $source -Destination $Destination
    }
    'apply' {
        (Invoke-MachineSoulApplyFile -Application $Application -Source $source -Destination $Destination -ConflictPolicy $ConflictPolicy).Status
    }
    'unapply' {
        (Invoke-MachineSoulUnapplyFile -Application $Application -Source $source -Destination $Destination).Status
    }
}
