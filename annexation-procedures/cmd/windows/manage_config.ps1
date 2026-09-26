param(
    [Parameter(Mandatory)]
    [ValidateSet('check','apply','unapply')]
    [string]$Action,

    [ValidateSet('prompt','abort','backup-and-replace')]
    [string]$ConflictPolicy = 'prompt'
)

$ErrorActionPreference = 'Stop'

$root = if ($env:MACHINE_SOUL) {
    $env:MACHINE_SOUL
} else {
    [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
}
$env:MACHINE_SOUL = $root

Import-Module "$root\accumulated-instruments\configuration-deployment\windows\MachineSoul.psm1" -Force

$hostName = if ($env:MACHINE_SOUL_HOST) {
    $env:MACHINE_SOUL_HOST.ToLowerInvariant()
} elseif ($env:COMPUTERNAME) {
    $env:COMPUTERNAME.ToLowerInvariant()
} else {
    'spaceship'
}

$sourceRel = "assimilation-directives\cmd\hosts\$hostName\common\cmdrc.cmd"
$source = Join-Path $root $sourceRel

$destination = if ($env:MACHINE_SOUL_CONFIG_DESTINATION) {
    $env:MACHINE_SOUL_CONFIG_DESTINATION
} else {
    Join-Path $env:LOCALAPPDATA 'MachineSoul\cmd\cmdrc.cmd'
}

$registryKey = if ($env:MACHINE_SOUL_CMD_REGISTRY_KEY) {
    $env:MACHINE_SOUL_CMD_REGISTRY_KEY
} else {
    'HKCU:\Software\Microsoft\Command Processor'
}

$expectedAutoRun = 'call "' + $destination + '"'
$stateDir = Get-MachineSoulScratchPath -RelativePath "state\cmd\$hostName\$(Get-MachineSoulAccount)" -CreateDirectory
$statePath = Join-Path $stateDir 'autorun.json'

function Get-AutoRunValue {
    if (-not (Test-Path -LiteralPath $registryKey)) {
        return $null
    }

    $item = Get-ItemProperty -LiteralPath $registryKey -Name AutoRun -ErrorAction SilentlyContinue
    if ($null -eq $item) {
        return $null
    }

    return [string]$item.AutoRun
}

function Save-CmdState {
    param([AllowNull()][string]$PriorAutoRun)

    $state = @{
        schema = 1
        registry_key = $registryKey
        expected_autorun = $expectedAutoRun
        had_prior_autorun = ($null -ne $PriorAutoRun)
        prior_autorun = $PriorAutoRun
    }

    $json = $state | ConvertTo-Json -Depth 3
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($statePath, $json, $utf8NoBom)
}

function Read-CmdState {
    if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
        return $null
    }
    return Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
}

$linkState = Get-MachineSoulConfigState -Source $source -Destination $destination
$currentAutoRun = Get-AutoRunValue

if ($Action -eq 'check') {
    if ($linkState -eq 'APPLIED' -and $currentAutoRun -eq $expectedAutoRun) {
        'APPLIED'
        exit 0
    }

    if ($linkState -eq 'NOT_APPLIED' -and $null -eq $currentAutoRun) {
        'NOT_APPLIED'
        exit 1
    }

    'CONFLICT'
    exit 1
}

if ($Action -eq 'apply') {
    if ($linkState -eq 'APPLIED' -and $currentAutoRun -eq $expectedAutoRun) {
        'APPLIED'
        exit 0
    }

    if ($null -ne $currentAutoRun -and $currentAutoRun -ne $expectedAutoRun) {
        if ($ConflictPolicy -eq 'abort') {
            'CONFLICT'
            exit 1
        }

        if ($ConflictPolicy -eq 'prompt') {
            $answer = Read-Host "CMD AutoRun already exists at '$registryKey'. Preserve and replace it? [y/N]"
            if ($answer -notmatch '^(?i:y|yes)$') {
                'CONFLICT'
                exit 1
            }
        }
    }

    $priorAutoRun = if ($currentAutoRun -eq $expectedAutoRun) { $null } else { $currentAutoRun }

    $linkResult = Invoke-MachineSoulApplyFile -Application 'cmd' -Source $source -Destination $destination -ConflictPolicy $ConflictPolicy
    if ($linkResult.Status -ne 'APPLIED') {
        $linkResult.Status
        exit 1
    }

    try {
        New-Item -ItemType Directory -Force -Path $registryKey | Out-Null
        Set-ItemProperty -LiteralPath $registryKey -Name AutoRun -Value $expectedAutoRun -Type String
        if ((Get-AutoRunValue) -ne $expectedAutoRun) {
            throw 'CMD AutoRun verification failed.'
        }

        if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
            Save-CmdState -PriorAutoRun $priorAutoRun
        }

        'APPLIED'
        exit 0
    } catch {
        Invoke-MachineSoulUnapplyFile -Application 'cmd' -Source $source -Destination $destination | Out-Null
        throw
    }
}

# unapply
$state = Read-CmdState
if ($currentAutoRun -ne $expectedAutoRun) {
    if ($linkState -eq 'NOT_APPLIED' -and $null -eq $currentAutoRun) {
        'NOT_APPLIED'
        exit 0
    }

    'CONFLICT'
    exit 1
}

if ($null -ne $state -and $state.had_prior_autorun) {
    Set-ItemProperty -LiteralPath $registryKey -Name AutoRun -Value ([string]$state.prior_autorun) -Type String
} else {
    Remove-ItemProperty -LiteralPath $registryKey -Name AutoRun -ErrorAction SilentlyContinue
}

$linkResult = Invoke-MachineSoulUnapplyFile -Application 'cmd' -Source $source -Destination $destination
if ($linkResult.Status -eq 'CONFLICT') {
    # Restore our AutoRun because the file side was not safe to unapply.
    Set-ItemProperty -LiteralPath $registryKey -Name AutoRun -Value $expectedAutoRun -Type String
    'CONFLICT'
    exit 1
}

Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
'NOT_APPLIED'
