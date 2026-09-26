param(
    [ValidateSet('prompt','abort','backup-and-replace')]
    [string]$ConflictPolicy = 'prompt'
)
$ErrorActionPreference = 'Stop'
$name = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
$action = switch ($name) {
    'apply_config' { 'apply' }
    'unapply_config' { 'unapply' }
    'check_config' { 'check' }
    default { throw "Unsupported operation entry point: $name" }
}
& (Join-Path $PSScriptRoot 'manage_config.ps1') -Action $action -ConflictPolicy $ConflictPolicy
