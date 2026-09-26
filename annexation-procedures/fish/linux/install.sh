#!/usr/bin/env bash
set -euo pipefail

dry_run=false
[[ "${1:-}" == "--dry-run" ]] && dry_run=true

root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)}"
export MACHINE_SOUL="$root"
# shellcheck source=../../../accumulated-instruments/configuration-deployment/linux/machine_soul.sh
source "$root/accumulated-instruments/configuration-deployment/linux/machine_soul.sh"

host="$(ms_host)"
account="$(ms_account)"
state_dir="$(ms_scratch_path "state/install/$host/$account" true)"
state="$state_dir/fish.state"

if command -v fish >/dev/null 2>&1; then
    if [[ -f "$state" ]]; then
        printf 'INSTALLED_MANAGED\n'
    else
        printf 'INSTALLED_UNMANAGED\n'
    fi
    exit 0
fi

command -v apt-get >/dev/null 2>&1 || { printf 'UNSUPPORTED\n'; exit 2; }

if $dry_run; then
    printf 'PLAN: install apt package fish\n'
    exit 0
fi

if [[ "$(id -u)" -eq 0 ]]; then
    apt-get install -y fish
elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get install -y fish
else
    printf 'ERROR: installing fish requires root privileges or sudo\n' >&2
    exit 3
fi

command -v fish >/dev/null 2>&1 || { printf 'ERROR: fish was not found after apt installation\n' >&2; exit 3; }

cat > "$state" <<EOF
schema=1
application=fish
manager=apt
package=fish
host=$host
account=$account
EOF

printf 'INSTALLED_MANAGED\n'
