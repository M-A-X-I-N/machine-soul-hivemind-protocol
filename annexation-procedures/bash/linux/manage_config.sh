#!/usr/bin/env bash
set -euo pipefail
action="$1"; shift
root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)}"
host="${MACHINE_SOUL_HOST:-$(hostname -s | tr '[:upper:]' '[:lower:]')}"
source_rel="assimilation-directives/bash/hosts/$host/common/.bashrc"
destination="${MACHINE_SOUL_CONFIG_DESTINATION:-$HOME/.bashrc}"
exec bash "$root/accumulated-instruments/configuration-deployment/linux/app_config.sh" "$action" bash "$source_rel" "$destination" "${1:-prompt}"
