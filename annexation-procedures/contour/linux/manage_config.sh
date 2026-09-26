#!/usr/bin/env bash
set -euo pipefail
action="$1"; shift
root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)}"
host="${MACHINE_SOUL_HOST:-$(hostname -s | tr '[:upper:]' '[:lower:]')}"
source_rel="assimilation-directives/contour/config/hosts/$host/common/contour.yml"
destination="${MACHINE_SOUL_CONFIG_DESTINATION:-${XDG_CONFIG_HOME:-$HOME/.config}/contour/contour.yml}"
exec bash "$root/accumulated-instruments/framework/linux/app_config.sh" "$action" contour "$source_rel" "$destination" "${1:-prompt}"
