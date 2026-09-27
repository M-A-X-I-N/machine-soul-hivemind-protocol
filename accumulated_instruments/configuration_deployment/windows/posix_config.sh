#!/usr/bin/env bash
set -euo pipefail

action="$1"
application="$2"
source_relative="$3"
destination_unix="$4"
policy="${5:-prompt}"

command -v cygpath >/dev/null 2>&1 || {
    printf 'UNSUPPORTED\n' >&2
    printf 'ERROR: Windows POSIX adapter requires cygpath (MSYS2/Cygwin compatible environment).\n' >&2
    exit 2
}
command -v powershell.exe >/dev/null 2>&1 || {
    printf 'UNSUPPORTED\n' >&2
    printf 'ERROR: Windows POSIX adapter requires powershell.exe.\n' >&2
    exit 2
}

root_unix="${MACHINE_SOUL:-}"
if [[ -z "$root_unix" ]]; then
    cursor="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
    while [[ "$cursor" != "/" ]]; do
        if [[ -f "$cursor/TASKS.md" && -f "$cursor/AGENTS.md" ]]; then
            root_unix="$cursor"
            break
        fi
        cursor="$(dirname "$cursor")"
    done
fi
[[ -n "$root_unix" ]] || {
    printf 'ERROR: unable to resolve MACHINE_SOUL\n' >&2
    exit 3
}

root_win="$(cygpath -w "$root_unix")"
destination_win="$(cygpath -w "$destination_unix")"
dispatcher_win="$(cygpath -w "$root_unix/accumulated_instruments/configuration_deployment/windows/invoke_app_config.ps1")"

export MACHINE_SOUL="$root_win"
export MACHINE_SOUL_HOST="${MACHINE_SOUL_HOST:-$(hostname -s | tr '[:upper:]' '[:lower:]')}"
export MACHINE_SOUL_ACCOUNT="${MACHINE_SOUL_ACCOUNT:-$(id -un)}"

# Prevent MSYS2/Git-Bash from rewriting already-converted Windows arguments.
export MSYS2_ARG_CONV_EXCL='*'

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$dispatcher_win"     -Action "$action"     -Application "$application"     -SourceRelative "$source_relative"     -Destination "$destination_win"     -ConflictPolicy "$policy"
