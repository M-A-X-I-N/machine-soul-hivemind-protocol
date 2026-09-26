#!/usr/bin/env bash
set -euo pipefail

dry_run=false
[[ "${1:-}" == "--dry-run" ]] && dry_run=true

root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)}"
export MACHINE_SOUL="$root"
# shellcheck source=../../../../accumulated-instruments/framework/linux/machine_soul.sh
source "$root/accumulated-instruments/framework/linux/machine_soul.sh"

host="$(ms_host)"
account="$(ms_account)"
state="$(ms_scratch_path "state/install/$host/$account")/fish.state"

if [[ ! -f "$state" ]]; then
    if command -v fish >/dev/null 2>&1; then
        printf 'INSTALLED_UNMANAGED\n'
        exit 1
    fi
    printf 'NOT_INSTALLED\n'
    exit 0
fi

command -v apt-get >/dev/null 2>&1 || { printf 'UNSUPPORTED\n'; exit 2; }

if $dry_run; then
    printf 'PLAN: uninstall managed apt package fish\n'
    exit 0
fi

if [[ "$(id -u)" -eq 0 ]]; then
    apt-get remove -y fish
elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get remove -y fish
else
    printf 'ERROR: uninstalling fish requires root privileges or sudo\n' >&2
    exit 3
fi

if command -v fish >/dev/null 2>&1; then
    printf 'ERROR: fish remains available after managed apt uninstall; refusing to erase provenance\n' >&2
    exit 3
fi

rm -f -- "$state"
printf 'NOT_INSTALLED\n'
