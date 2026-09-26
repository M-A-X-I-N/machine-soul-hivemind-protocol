#!/usr/bin/env bash
set -euo pipefail

action="$1"
application="$2"
source_relative="$3"
destination="$4"
policy="${5:-prompt}"

repo_root="${MACHINE_SOUL:-}"
if [[ -z "$repo_root" ]]; then
    cursor="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
    while [[ "$cursor" != "/" ]]; do
        if [[ -f "$cursor/TASKS.md" && -f "$cursor/AGENTS.md" ]]; then
            repo_root="$cursor"
            export MACHINE_SOUL="$repo_root"
            break
        fi
        cursor="$(dirname "$cursor")"
    done
fi
[[ -n "$repo_root" ]] || { printf 'ERROR: unable to resolve MACHINE_SOUL\n' >&2; exit 3; }

# shellcheck source=machine_soul.sh
source "$repo_root/accumulated-instruments/framework/linux/machine_soul.sh"
source_path="$repo_root/$source_relative"

case "$action" in
    check)
        ms_config_state "$source_path" "$destination"
        ;;
    apply)
        ms_apply_file "$application" "$source_path" "$destination" "$policy"
        ;;
    unapply)
        ms_unapply_file "$application" "$source_path" "$destination"
        ;;
    *)
        printf 'ERROR: unknown action: %s\n' "$action" >&2
        exit 3
        ;;
esac
