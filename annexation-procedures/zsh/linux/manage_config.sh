#!/usr/bin/env bash
set -euo pipefail
action="$1"; shift
root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)}"
host="${MACHINE_SOUL_HOST:-$(hostname -s | tr '[:upper:]' '[:lower:]')}"
source_rel="assimilation-directives/zsh/config/hosts/$host/common/.zshrc"
destination="${MACHINE_SOUL_CONFIG_DESTINATION:-$HOME/.zshrc}"
exec bash "$root/accumulated-instruments/framework/linux/app_config.sh" "$action" zsh "$source_rel" "$destination" "${1:-prompt}"
