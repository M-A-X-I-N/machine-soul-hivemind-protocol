#!/usr/bin/env bash
set -euo pipefail

actual_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
# shellcheck source=../../accumulated-instruments/configuration-deployment/linux/machine_soul.sh
source "$actual_repo/accumulated-instruments/configuration-deployment/linux/machine_soul.sh"

tmp="$(mktemp -d)"
old_root="$tmp/old-soul"
new_root="$tmp/new-soul"
destination="$tmp/native/config.file"

cleanup() {
    rm -rf -- "$tmp"
}
trap cleanup EXIT

mkdir -p "$old_root/config" "$(dirname "$destination")"
printf '# marker\n' > "$old_root/TASKS.md"
printf 'canonical\n' > "$old_root/config/canonical.conf"
printf 'original\n' > "$destination"

export MACHINE_SOUL="$old_root"
export MACHINE_SOUL_HOST="relocation-linux"
export MACHINE_SOUL_ACCOUNT="tester"

[[ "$(ms_apply_file relocation-test "$old_root/config/canonical.conf" "$destination" backup-and-replace)" == "APPLIED" ]]
[[ "$(cat "$destination")" == "canonical" ]]

mv -- "$old_root" "$new_root"
export MACHINE_SOUL="$new_root"

state="$(ms_config_state "$new_root/config/canonical.conf" "$destination")"
[[ "$state" == "BROKEN" || "$state" == "WRONG_TARGET" ]] || {
    printf 'Expected stale link after checkout relocation, got: %s\n' "$state" >&2
    exit 1
}

[[ "$(ms_apply_file relocation-test "$new_root/config/canonical.conf" "$destination" abort)" == "APPLIED" ]]
[[ "$(ms_config_state "$new_root/config/canonical.conf" "$destination")" == "APPLIED" ]]
[[ "$(cat "$destination")" == "canonical" ]]

[[ "$(ms_unapply_file relocation-test "$new_root/config/canonical.conf" "$destination")" == "NOT_APPLIED" ]]
[[ ! -L "$destination" ]]
[[ "$(cat "$destination")" == "original" ]]

printf 'Linux relocation/restore-lineage test passed.\n'
