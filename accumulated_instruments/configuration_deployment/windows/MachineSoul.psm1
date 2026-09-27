Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-MachineSoulRoot {
    [CmdletBinding()]
    param([string]$StartPath = $PSScriptRoot)

    if ($env:MACHINE_SOUL) {
        $candidate = [System.IO.Path]::GetFullPath($env:MACHINE_SOUL)
        if (Test-Path -LiteralPath (Join-Path $candidate '.machine_soul_root') -PathType Leaf) {
            return $candidate
        }
        throw "MACHINE_SOUL points to '$candidate', but .machine_soul_root was not found there."
    }

    $cursor = [System.IO.DirectoryInfo][System.IO.Path]::GetFullPath($StartPath)
    while ($null -ne $cursor) {
        if (Test-Path -LiteralPath (Join-Path $cursor.FullName '.machine_soul_root') -PathType Leaf) {
            $env:MACHINE_SOUL = $cursor.FullName
            return $cursor.FullName
        }
        $cursor = $cursor.Parent
    }

    throw 'Unable to resolve MACHINE_SOUL from the environment or repository ancestry.'
}

function Get-MachineSoulHost {
    if ($env:MACHINE_SOUL_HOST) {
        return $env:MACHINE_SOUL_HOST.ToLowerInvariant()
    }

    if ($env:COMPUTERNAME) {
        return $env:COMPUTERNAME.ToLowerInvariant()
    }

    return ([System.Net.Dns]::GetHostName()).Split('.')[0].ToLowerInvariant()
}

function Get-MachineSoulAccount {
    if ($env:MACHINE_SOUL_ACCOUNT) {
        return $env:MACHINE_SOUL_ACCOUNT
    }

    if ($env:USERNAME) {
        return $env:USERNAME
    }

    return [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
}

function Get-MachineSoulScratchPath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$RelativePath,
        [switch]$CreateDirectory
    )

    $root = Get-MachineSoulRoot
    $path = Join-Path (Join-Path $root 'scratch') $RelativePath
    if ($CreateDirectory) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
    return $path
}

function Get-MachineSoulPathHash {
    param([Parameter(Mandatory)][string]$Path)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes([System.IO.Path]::GetFullPath($Path))
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($bytes)
    } finally {
        $sha.Dispose()
    }
    return (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}

function Resolve-MachineSoulLinkTarget {
    param(
        [Parameter(Mandatory)][string]$Destination,
        [Parameter(Mandatory)][string]$RawTarget
    )

    if ([System.IO.Path]::IsPathRooted($RawTarget)) {
        return [System.IO.Path]::GetFullPath($RawTarget)
    }

    $parent = Split-Path -Parent ([System.IO.Path]::GetFullPath($Destination))
    return [System.IO.Path]::GetFullPath((Join-Path $parent $RawTarget))
}

function Get-MachineSoulLinkInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination
    )

    $expected = [System.IO.Path]::GetFullPath($Source)
    $dest = [System.IO.Path]::GetFullPath($Destination)

    $item = Get-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) {
        return [pscustomobject]@{
            Status = 'NOT_APPLIED'
            ExpectedTarget = $expected
            ActualTarget = $null
            IsExpectedLink = $false
            Destination = $dest
        }
    }

    if ($item.LinkType -eq 'SymbolicLink') {
        $rawTarget = if ($item.Target -is [array]) { [string]$item.Target[0] } else { [string]$item.Target }
        $actual = Resolve-MachineSoulLinkTarget -Destination $dest -RawTarget $rawTarget
        $isExpected = [System.StringComparer]::OrdinalIgnoreCase.Equals($actual, $expected)
        $targetExists = Test-Path -LiteralPath $actual -PathType Leaf

        $status = if ($isExpected -and $targetExists) {
            'APPLIED'
        } elseif (-not $targetExists) {
            'BROKEN'
        } else {
            'WRONG_TARGET'
        }

        return [pscustomobject]@{
            Status = $status
            ExpectedTarget = $expected
            ActualTarget = $actual
            RawTarget = $rawTarget
            IsExpectedLink = $isExpected
            Destination = $dest
        }
    }

    return [pscustomobject]@{
        Status = 'CONFLICT'
        ExpectedTarget = $expected
        ActualTarget = $null
        IsExpectedLink = $false
        Destination = $dest
        ExistingType = if ($item.PSIsContainer) { 'directory' } else { 'file' }
    }
}

function Get-MachineSoulConfigState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination
    )

    return (Get-MachineSoulLinkInfo -Source $Source -Destination $Destination).Status
}

function Get-MachineSoulStatePath {
    param(
        [Parameter(Mandatory)][string]$Application,
        [Parameter(Mandatory)][string]$Destination
    )

    $hostName = Get-MachineSoulHost
    $account = Get-MachineSoulAccount
    $hash = Get-MachineSoulPathHash -Path $Destination
    $dir = Get-MachineSoulScratchPath -RelativePath (Join-Path 'state/config' (Join-Path $hostName (Join-Path $account $Application))) -CreateDirectory
    return Join-Path $dir "$hash.json"
}

function Save-MachineSoulState {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][hashtable]$State
    )

    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $temp = "$Path.tmp-$PID"
    $json = $State | ConvertTo-Json -Depth 5
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temp, $json, $utf8NoBom)
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Read-MachineSoulState {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Invoke-MachineSoulApplyFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Application,
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination,
        [ValidateSet('prompt','abort','backup-and-replace')]
        [string]$ConflictPolicy = 'prompt'
    )

    $sourcePath = [System.IO.Path]::GetFullPath($Source)
    $destPath = [System.IO.Path]::GetFullPath($Destination)

    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Canonical source file does not exist: $sourcePath"
    }

    $info = Get-MachineSoulLinkInfo -Source $sourcePath -Destination $destPath
    if ($info.Status -eq 'APPLIED') {
        return [pscustomobject]@{ Status = 'APPLIED'; Changed = $false }
    }

    # A moved MACHINE_SOUL checkout changes the concrete symlink target.
    # If state proves this stale link is the one we created, repair it while
    # preserving the original pre-managed restore lineage.
    if (($info.Status -eq 'WRONG_TARGET' -or $info.Status -eq 'BROKEN') -and $info.ActualTarget) {
        $relocationStatePath = Get-MachineSoulStatePath -Application $Application -Destination $destPath
        $relocationState = Read-MachineSoulState -Path $relocationStatePath
        if ($null -ne $relocationState -and $relocationState.applied_target -and $relocationState.source_relative) {
            $root = Get-MachineSoulRoot
            $relocatedSource = [System.IO.Path]::GetFullPath((Join-Path $root $relocationState.source_relative))
            $ownedOldTarget = [System.StringComparer]::OrdinalIgnoreCase.Equals(
                [System.IO.Path]::GetFullPath([string]$relocationState.applied_target),
                [System.IO.Path]::GetFullPath([string]$info.ActualTarget)
            )
            $sameLogicalSource = [System.StringComparer]::OrdinalIgnoreCase.Equals($relocatedSource, $sourcePath)

            if ($ownedOldTarget -and $sameLogicalSource) {
                $item = Get-Item -LiteralPath $destPath -Force -ErrorAction Stop
                $rawOldTarget = if ($item.Target -is [array]) { [string]$item.Target[0] } else { [string]$item.Target }

                Remove-Item -LiteralPath $destPath -Force
                try {
                    New-Item -ItemType SymbolicLink -Path $destPath -Target $sourcePath | Out-Null
                    $verifyRelocation = Get-MachineSoulLinkInfo -Source $sourcePath -Destination $destPath
                    if ($verifyRelocation.Status -ne 'APPLIED') {
                        throw "Relocated symlink repair verification failed with state $($verifyRelocation.Status)."
                    }
                } catch {
                    Remove-Item -LiteralPath $destPath -Force -ErrorAction SilentlyContinue
                    New-Item -ItemType SymbolicLink -Path $destPath -Target $rawOldTarget | Out-Null
                    throw
                }

                Save-MachineSoulState -Path $relocationStatePath -State @{
                    schema = 1
                    application = [string]$relocationState.application
                    host = [string]$relocationState.host
                    account = [string]$relocationState.account
                    source_relative = [string]$relocationState.source_relative
                    destination = [string]$relocationState.destination
                    prior_type = [string]$relocationState.prior_type
                    backup_relative = [string]$relocationState.backup_relative
                    backup = if ($relocationState.backup_relative) {
                        Join-Path $root ([string]$relocationState.backup_relative)
                    } else {
                        [string]$relocationState.backup
                    }
                    prior_target = [string]$relocationState.prior_target
                    applied_target = $sourcePath
                    applied_utc = [DateTime]::UtcNow.ToString('o')
                }

                return [pscustomobject]@{ Status = 'APPLIED'; Changed = $true }
            }
        }
    }

    $priorType = 'absent'
    $priorTarget = $null
    $backupPath = $null

    if ($info.Status -ne 'NOT_APPLIED') {
        $item = Get-Item -LiteralPath $destPath -Force -ErrorAction SilentlyContinue
        if ($null -ne $item -and $item.PSIsContainer -and $item.LinkType -ne 'SymbolicLink') {
            throw "Destination is a directory and cannot be replaced as a managed config file: $destPath"
        }

        if ($ConflictPolicy -eq 'abort') {
            return [pscustomobject]@{ Status = 'CONFLICT'; Changed = $false }
        }

        if ($ConflictPolicy -eq 'prompt') {
            $answer = Read-Host "Existing unmanaged configuration detected at '$destPath'. Preserve and replace it? [y/N]"
            if ($answer -notmatch '^(?i:y|yes)$') {
                return [pscustomobject]@{ Status = 'CONFLICT'; Changed = $false }
            }
        }

        if ($null -ne $item -and $item.LinkType -eq 'SymbolicLink') {
            $priorType = 'symlink'
            $priorTarget = if ($item.Target -is [array]) { [string]$item.Target[0] } else { [string]$item.Target }
            Remove-Item -LiteralPath $destPath -Force
        } else {
            $priorType = 'file'
            $hostName = Get-MachineSoulHost
            $account = Get-MachineSoulAccount
            $hash = Get-MachineSoulPathHash -Path $destPath
            $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
            $backupDir = Get-MachineSoulScratchPath -RelativePath (Join-Path 'backups' (Join-Path $hostName (Join-Path $account (Join-Path $Application "$stamp-$hash")))) -CreateDirectory
            $backupPath = Join-Path $backupDir 'original'
            Move-Item -LiteralPath $destPath -Destination $backupPath
        }
    }

    $parent = Split-Path -Parent $destPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    try {
        New-Item -ItemType SymbolicLink -Path $destPath -Target $sourcePath | Out-Null
        $verify = Get-MachineSoulLinkInfo -Source $sourcePath -Destination $destPath
        if ($verify.Status -ne 'APPLIED') {
            throw "Symlink verification failed with state $($verify.Status)."
        }
    } catch {
        if (Get-Item -LiteralPath $destPath -Force -ErrorAction SilentlyContinue) {
            Remove-Item -LiteralPath $destPath -Force -ErrorAction SilentlyContinue
        }

        if ($priorType -eq 'file' -and $backupPath -and (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
            Move-Item -LiteralPath $backupPath -Destination $destPath
        } elseif ($priorType -eq 'symlink') {
            New-Item -ItemType SymbolicLink -Path $destPath -Target $priorTarget | Out-Null
        }

        throw
    }

    $root = Get-MachineSoulRoot
    $statePath = Get-MachineSoulStatePath -Application $Application -Destination $destPath
    $backupRelative = $null
    if ($backupPath -and $backupPath.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        $backupRelative = $backupPath.Substring($root.Length).TrimStart([char[]]@('\', '/'))
    }

    Save-MachineSoulState -Path $statePath -State @{
        schema = 2
        application = $Application
        host = Get-MachineSoulHost
        account = Get-MachineSoulAccount
        source_relative = if ($sourcePath.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
            $sourcePath.Substring($root.Length).TrimStart([char[]]@('\', '/'))
        } else {
            $sourcePath
        }
        destination = $destPath
        prior_type = $priorType
        backup_relative = $backupRelative
        backup = $backupPath
        prior_target = $priorTarget
        applied_target = $sourcePath
        applied_utc = [DateTime]::UtcNow.ToString('o')
    }

    return [pscustomobject]@{ Status = 'APPLIED'; Changed = $true }
}

function Invoke-MachineSoulUnapplyFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Application,
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination
    )

    $sourcePath = [System.IO.Path]::GetFullPath($Source)
    $destPath = [System.IO.Path]::GetFullPath($Destination)
    $info = Get-MachineSoulLinkInfo -Source $sourcePath -Destination $destPath

    if ($info.Status -eq 'NOT_APPLIED') {
        return [pscustomobject]@{ Status = 'NOT_APPLIED'; Changed = $false }
    }

    if (-not $info.IsExpectedLink) {
        return [pscustomobject]@{ Status = 'CONFLICT'; Changed = $false }
    }

    $statePath = Get-MachineSoulStatePath -Application $Application -Destination $destPath
    $state = Read-MachineSoulState -Path $statePath

    Remove-Item -LiteralPath $destPath -Force

    if ($null -ne $state) {
        if ($state.prior_type -eq 'file') {
            $resolvedBackup = if ($state.backup_relative) {
                Join-Path (Get-MachineSoulRoot) ([string]$state.backup_relative)
            } else {
                [string]$state.backup
            }

            if ($resolvedBackup -and (Test-Path -LiteralPath $resolvedBackup -PathType Leaf)) {
                Move-Item -LiteralPath $resolvedBackup -Destination $destPath
            } else {
                throw "Managed link was removed, but recorded backup is missing: $resolvedBackup"
            }
        } elseif ($state.prior_type -eq 'symlink' -and $state.prior_target) {
            New-Item -ItemType SymbolicLink -Path $destPath -Target $state.prior_target | Out-Null
        }

        Remove-Item -LiteralPath $statePath -Force -ErrorAction SilentlyContinue
    }

    return [pscustomobject]@{ Status = 'NOT_APPLIED'; Changed = $true }
}

Export-ModuleMember -Function @(
    'Get-MachineSoulRoot',
    'Get-MachineSoulHost',
    'Get-MachineSoulAccount',
    'Get-MachineSoulScratchPath',
    'Get-MachineSoulConfigState',
    'Get-MachineSoulLinkInfo',
    'Invoke-MachineSoulApplyFile',
    'Invoke-MachineSoulUnapplyFile'
)
