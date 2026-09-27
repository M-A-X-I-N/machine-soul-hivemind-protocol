#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="ci-install-linux"
export MACHINE_SOUL_ACCOUNT="ci-user"

cleanup() {
    rm -rf -- "$repo_root/scratch/state/install/ci-install-linux"
}
trap cleanup EXIT

state="$repo_root/scratch/state/install/ci-install-linux/ci-user/fish.state"
output="$("$repo_root/annexation_procedures/fish/linux/install.sh" --dry-run)"

if command -v fish >/dev/null 2>&1; then
    [[ "$output" == "INSTALLED_UNMANAGED" ]] || {
        printf 'Expected unmanaged Fish on preinstalled runner, got: %s\n' "$output" >&2
        exit 1
    }
else
    [[ "$output" == "PLAN: install apt package fish" ]] || {
        printf 'Unexpected Fish dry-run output: %s\n' "$output" >&2
        exit 1
    }
fi

[[ ! -f "$state" ]] || {
    printf 'Dry-run or unmanaged detection must not claim Fish installation ownership.\n' >&2
    exit 1
}

printf 'Linux installation dry-run/provenance test passed.\n'
