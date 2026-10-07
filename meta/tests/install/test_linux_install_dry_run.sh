#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="ci_install_linux"
unset MACHINE_SOUL_ACCOUNT || true

cleanup() {
    rm -rf -- "$repo_root/scratch/state/install/ci_install_linux"
}
trap cleanup EXIT

set +e
output="$(python3 "$repo_root/annexation/fish/install.py" --dry-run --json)"
status=$?
set -e
[[ $status -le 3 ]]
code="$(printf '%s' "$output" | python3 -c 'import json,sys; print(json.load(sys.stdin)["code"])')"

if command -v fish >/dev/null 2>&1; then
    [[ "$code" == "installed_unmanaged" ]] || {
        printf 'Expected unmanaged Fish on preinstalled runner, got: %s\n' "$code" >&2
        exit 1
    }
else
    [[ "$code" == "would_install" ]] || {
        printf 'Unexpected Fish dry-run result: %s\n' "$code" >&2
        exit 1
    }
fi

if find "$repo_root/scratch/state/install/ci_install_linux" -type f -print -quit 2>/dev/null | grep -q .; then
    printf 'Dry-run or unmanaged detection must not claim Fish installation ownership.\n' >&2
    exit 1
fi

printf 'Linux Python installation dry-run/provenance test passed.\n'
