#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp="$(mktemp -d)"
soul="$tmp/soul"
normal_user="$(id -un)"
host="fixture_host"
normal_dest="$tmp/native/normal/theme.omp.json"
root_dest="$tmp/native/root/theme.omp.json"
wrapper="$repo_root/annexation_procedures/oh_my_posh"

cleanup() {
    sudo rm -rf -- "$tmp" 2>/dev/null || rm -rf -- "$tmp"
}
trap cleanup EXIT

mkdir -p "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/$normal_user"
mkdir -p "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/root"
mkdir -p "$(dirname "$normal_dest")" "$(dirname "$root_dest")"
printf 'Machine-Soul repository root\n' > "$soul/.machine_soul_root"
printf 'normal\n' > "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/$normal_user/theme.omp.json"
printf 'root\n' > "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/root/theme.omp.json"

json_code() {
    python3 -c 'import json,sys; print(json.load(sys.stdin)["code"])'
}

normal_output="$(
    env -i         HOME="$HOME"         PATH="$PATH"         MACHINE_SOUL="$soul"         MACHINE_SOUL_HOST="$host"         MACHINE_SOUL_CONFIG_DESTINATION="$normal_dest"         python3 "$wrapper/apply_config.py" --account "$normal_user" --conflict-policy abort --json
)"
[[ "$(printf '%s' "$normal_output" | json_code)" == "applied" ]]
normal_target="$(readlink -- "$normal_dest")"
[[ "$normal_target" == "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/$normal_user/theme.omp.json" ]]

sudo env     MACHINE_SOUL="$soul"     MACHINE_SOUL_HOST="$host"     MACHINE_SOUL_CONFIG_DESTINATION="$root_dest"     PATH="$PATH"     python3 "$wrapper/apply_config.py" --account root --conflict-policy abort --json >/tmp/machine-soul-root-apply.json

[[ "$(json_code </tmp/machine-soul-root-apply.json)" == "applied" ]]
root_target="$(readlink -- "$root_dest")"
[[ "$root_target" == "$soul/assimilation_directives/oh_my_posh/hosts/$host/users/root/theme.omp.json" ]]

sudo env     MACHINE_SOUL="$soul"     MACHINE_SOUL_HOST="$host"     MACHINE_SOUL_CONFIG_DESTINATION="$root_dest"     PATH="$PATH"     python3 "$wrapper/unapply_config.py" --account root --json >/tmp/machine-soul-root-unapply.json
[[ "$(json_code </tmp/machine-soul-root-unapply.json)" == "not_applied" ]]

env     MACHINE_SOUL="$soul"     MACHINE_SOUL_HOST="$host"     MACHINE_SOUL_CONFIG_DESTINATION="$normal_dest"     python3 "$wrapper/unapply_config.py" --account "$normal_user" --json >/tmp/machine-soul-user-unapply.json
[[ "$(json_code </tmp/machine-soul-user-unapply.json)" == "not_applied" ]]

rm -f /tmp/machine-soul-root-apply.json /tmp/machine-soul-root-unapply.json /tmp/machine-soul-user-unapply.json
printf 'Linux explicit target-account boundary test passed.\n'
