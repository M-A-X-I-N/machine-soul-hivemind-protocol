#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
# shellcheck source=../../accumulated_instruments/configuration_deployment/linux/machine_soul.sh
source "$repo_root/accumulated_instruments/configuration_deployment/linux/machine_soul.sh"

export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="ci-linux"
export MACHINE_SOUL_ACCOUNT="ci-user"

tmp="$(mktemp -d)"
cleanup() {
    rm -rf -- "$tmp"
    rm -rf -- "$repo_root/scratch/state/config/ci-linux" "$repo_root/scratch/backups/ci-linux"
}
trap cleanup EXIT

assert_eq() {
    local expected="$1"
    local actual="$2"
    local message="$3"
    if [[ "$expected" != "$actual" ]]; then
        printf 'ASSERTION FAILED: %s\nexpected: %s\nactual:   %s\n' "$message" "$expected" "$actual" >&2
        exit 1
    fi
}

source_file="$tmp/canonical.conf"
destination="$tmp/native/config.conf"
mkdir -p "$(dirname "$destination")"
printf 'canonical\n' > "$source_file"

assert_eq "NOT_APPLIED" "$(ms_config_state "$source_file" "$destination")" "initial state"
assert_eq "APPLIED" "$(ms_apply_file test-app "$source_file" "$destination" abort)" "first apply"
assert_eq "APPLIED" "$(ms_config_state "$source_file" "$destination")" "state after apply"
assert_eq "APPLIED" "$(ms_apply_file test-app "$source_file" "$destination" abort)" "idempotent apply"
assert_eq "NOT_APPLIED" "$(ms_unapply_file test-app "$source_file" "$destination")" "unapply"
assert_eq "NOT_APPLIED" "$(ms_config_state "$source_file" "$destination")" "state after unapply"

printf 'original\n' > "$destination"
assert_eq "CONFLICT" "$(ms_config_state "$source_file" "$destination")" "regular file conflict"
set +e
abort_output="$(ms_apply_file test-app "$source_file" "$destination" abort)"
abort_code=$?
set -e
assert_eq "1" "$abort_code" "abort conflict exit code"
assert_eq "CONFLICT" "$abort_output" "abort conflict status"
assert_eq "original" "$(cat "$destination")" "abort preserves original"

assert_eq "APPLIED" "$(ms_apply_file test-app "$source_file" "$destination" backup-and-replace)" "apply over existing file"
assert_eq "canonical" "$(cat "$destination")" "managed link resolves canonical content"
assert_eq "NOT_APPLIED" "$(ms_unapply_file test-app "$source_file" "$destination")" "unapply restores original"
assert_eq "original" "$(cat "$destination")" "original file restored"

wrong_target="$tmp/wrong.conf"
printf 'wrong\n' > "$wrong_target"
rm -f -- "$destination"
ln -s -- "$wrong_target" "$destination"
assert_eq "WRONG_TARGET" "$(ms_config_state "$source_file" "$destination")" "wrong target state"
rm -f -- "$wrong_target"
assert_eq "BROKEN" "$(ms_config_state "$source_file" "$destination")" "broken target state"


# Interactive decline must preserve unmanaged content.
rm -f -- "$destination"
printf 'decline-me\n' > "$destination"
set +e
decline_output="$(printf 'n\n' | ms_apply_file test-app "$source_file" "$destination" prompt)"
decline_code=$?
set -e
assert_eq "1" "$decline_code" "prompt decline exit code"
assert_eq "CONFLICT" "$decline_output" "prompt decline status"
assert_eq "decline-me" "$(cat "$destination")" "prompt decline preserves original"

# If a human replaces our managed link, Unapply must refuse to overwrite it.
assert_eq "APPLIED" "$(ms_apply_file test-app "$source_file" "$destination" backup-and-replace)" "apply before external mutation"
rm -f -- "$destination"
printf 'human-new-state\n' > "$destination"
set +e
external_output="$(ms_unapply_file test-app "$source_file" "$destination")"
external_code=$?
set -e
assert_eq "1" "$external_code" "external mutation conflict exit"
assert_eq "CONFLICT" "$external_output" "external mutation conflict status"
assert_eq "human-new-state" "$(cat "$destination")" "external mutation is preserved"
rm -f -- "$destination"

printf 'Linux framework tests passed.\n'
