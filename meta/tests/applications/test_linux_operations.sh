#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="workhorse"
unset MACHINE_SOUL_ACCOUNT || true

tmp="$(mktemp -d)"
cleanup() {
    rm -rf -- "$tmp"
    rm -rf -- "$repo_root/scratch/state/config/workhorse" "$repo_root/scratch/backups/workhorse"
}
trap cleanup EXIT

result_code() {
    local wrapper="$1"
    shift
    local output status
    set +e
    output="$(python3 "$wrapper" --json "$@")"
    status=$?
    set -e
    [[ $status -le 3 ]] || return "$status"
    printf '%s' "$output" | python3 -c 'import json,sys; print(json.load(sys.stdin)["code"])'
}

assert_eq() {
    [[ "$1" == "$2" ]] || {
        printf 'ASSERTION FAILED: %s\nexpected: %s\nactual:   %s\n' "$3" "$1" "$2" >&2
        exit 1
    }
}

for app in fish bash zsh oh_my_posh contour; do
    export MACHINE_SOUL_CONFIG_DESTINATION="$tmp/$app/config.file"
    mkdir -p "$(dirname "$MACHINE_SOUL_CONFIG_DESTINATION")"

    ops="$repo_root/annexation/$app"
    account_args=()
    if [[ "$app" == "oh_my_posh" ]]; then
        account_args=(--account root)
    fi

    assert_eq "not_applied" "$(result_code "$ops/check_config.py" "${account_args[@]}")" "$app initial check"
    assert_eq "applied" "$(result_code "$ops/apply_config.py" "${account_args[@]}" --conflict-policy abort)" "$app apply"
    assert_eq "applied" "$(result_code "$ops/check_config.py" "${account_args[@]}")" "$app check applied"
    assert_eq "applied" "$(result_code "$ops/apply_config.py" "${account_args[@]}" --conflict-policy abort)" "$app idempotent apply"
    assert_eq "not_applied" "$(result_code "$ops/unapply_config.py" "${account_args[@]}")" "$app unapply"
    assert_eq "not_applied" "$(result_code "$ops/check_config.py" "${account_args[@]}")" "$app final check"
done

printf 'Linux Python-wrapper application operation tests passed.\n'
