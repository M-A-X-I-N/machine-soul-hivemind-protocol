#!/usr/bin/env bash
set -euo pipefail
action="$1"; shift
root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)}"
host="${MACHINE_SOUL_HOST:-$(hostname -s | tr '[:upper:]' '[:lower:]')}"
account="${MACHINE_SOUL_ACCOUNT:-$(id -un)}"
user_rel="assimilation-directives/oh-my-posh/hosts/$host/users/$account/theme.omp.json"
common_rel="assimilation-directives/oh-my-posh/hosts/$host/common/theme.omp.json"
if [[ -f "$root/$user_rel" ]]; then source_rel="$user_rel"; else source_rel="$common_rel"; fi
destination="${MACHINE_SOUL_CONFIG_DESTINATION:-${XDG_CONFIG_HOME:-$HOME/.config}/oh-my-posh/theme.omp.json}"
exec bash "$root/accumulated-instruments/configuration-deployment/linux/app_config.sh" "$action" oh-my-posh "$source_rel" "$destination" "${1:-prompt}"
