#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp="$(mktemp -d)"
normal_dest="$tmp/normal/theme.omp.json"
root_dest="$tmp/root/theme.omp.json"

cleanup() {
    rm -rf -- "$tmp"
    rm -rf -- "$repo_root/scratch/state/config/workhorse/m-a-x-i-n" "$repo_root/scratch/backups/workhorse/m-a-x-i-n"
    sudo rm -rf -- "$repo_root/scratch/state/config/workhorse/root" "$repo_root/scratch/backups/workhorse/root" 2>/dev/null || true
}
trap cleanup EXIT

normal_ops="$repo_root/annexation_procedures/oh_my_posh/linux"

# SSH-like boundary: a fresh non-login process receives only the remote machine's
# own MACHINE_SOUL/host/account context; it does not inherit a local shell prompt.
normal_output="$(
    env -i         HOME="$HOME"         PATH="$PATH"         MACHINE_SOUL="$repo_root"         MACHINE_SOUL_HOST="workhorse"         MACHINE_SOUL_ACCOUNT="m-a-x-i-n"         MACHINE_SOUL_CONFIG_DESTINATION="$normal_dest"         bash --noprofile --norc "$normal_ops/apply_config.sh" abort
)"
[[ "$normal_output" == "APPLIED" ]]
normal_target="$(readlink -- "$normal_dest")"
[[ "$normal_target" == *"/assimilation_directives/oh_my_posh/hosts/workhorse/users/m-a-x-i-n/theme.omp.json" ]] || {
    printf 'Normal account resolved wrong OMP target: %s\n' "$normal_target" >&2
    exit 1
}

# Actual sudo boundary: root is a different process/account and resolves root's
# independent OMP configuration while sharing the same repository.
sudo env     MACHINE_SOUL="$repo_root"     MACHINE_SOUL_HOST="workhorse"     MACHINE_SOUL_ACCOUNT="root"     MACHINE_SOUL_CONFIG_DESTINATION="$root_dest"     PATH="$PATH"     bash "$normal_ops/apply_config.sh" abort >/tmp/machine-soul-root-apply.out

[[ "$(cat /tmp/machine-soul-root-apply.out)" == "APPLIED" ]]
root_target="$(readlink -- "$root_dest")"
[[ "$root_target" == *"/assimilation_directives/oh_my_posh/hosts/workhorse/users/root/theme.omp.json" ]] || {
    printf 'Root account resolved wrong OMP target: %s\n' "$root_target" >&2
    exit 1
}

# Root-created link/state must be un-applied as root; normal-user state remains
# independently manageable.
sudo env     MACHINE_SOUL="$repo_root"     MACHINE_SOUL_HOST="workhorse"     MACHINE_SOUL_ACCOUNT="root"     MACHINE_SOUL_CONFIG_DESTINATION="$root_dest"     PATH="$PATH"     bash "$normal_ops/unapply_config.sh" >/tmp/machine-soul-root-unapply.out
[[ "$(cat /tmp/machine-soul-root-unapply.out)" == "NOT_APPLIED" ]]

env     MACHINE_SOUL="$repo_root"     MACHINE_SOUL_HOST="workhorse"     MACHINE_SOUL_ACCOUNT="m-a-x-i-n"     MACHINE_SOUL_CONFIG_DESTINATION="$normal_dest"     bash "$normal_ops/unapply_config.sh" >/tmp/machine-soul-user-unapply.out
[[ "$(cat /tmp/machine-soul-user-unapply.out)" == "NOT_APPLIED" ]]

rm -f /tmp/machine-soul-root-apply.out /tmp/machine-soul-root-unapply.out /tmp/machine-soul-user-unapply.out
printf 'Linux session/account boundary test passed.\n'
