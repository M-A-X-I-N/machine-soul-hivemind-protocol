#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="workhorse"
export MACHINE_SOUL_ACCOUNT="m-a-x-i-n"

tmp="$(mktemp -d)"
cleanup() {
    rm -rf -- "$tmp"
    rm -rf -- "$repo_root/scratch/state/config/workhorse" "$repo_root/scratch/backups/workhorse"
}
trap cleanup EXIT

assert_eq() {
    [[ "$1" == "$2" ]] || {
        printf 'ASSERTION FAILED: %s\nexpected: %s\nactual:   %s\n' "$3" "$1" "$2" >&2
        exit 1
    }
}

for app in fish bash zsh oh-my-posh contour; do
    export MACHINE_SOUL_CONFIG_DESTINATION="$tmp/$app/config.file"
    mkdir -p "$(dirname "$MACHINE_SOUL_CONFIG_DESTINATION")"

    ops="$repo_root/annexation_procedures/$app/linux"
    assert_eq "NOT_APPLIED" "$("$ops/check_config.sh")" "$app initial check"
    assert_eq "APPLIED" "$("$ops/apply_config.sh" abort)" "$app apply"
    assert_eq "APPLIED" "$("$ops/check_config.sh")" "$app check applied"
    assert_eq "APPLIED" "$("$ops/apply_config.sh" abort)" "$app idempotent apply"
    assert_eq "NOT_APPLIED" "$("$ops/unapply_config.sh")" "$app unapply"
    assert_eq "NOT_APPLIED" "$("$ops/check_config.sh")" "$app final check"
done

printf 'Linux application operation tests passed.\n'
