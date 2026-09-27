#!/usr/bin/env bash
set -euo pipefail
action="$1"; shift
root="${MACHINE_SOUL:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)}"
host="${MACHINE_SOUL_HOST:-spaceship}"
source_rel="assimilation_directives\\zsh\\hosts\\$host\\common\\.zshrc"
destination="${MACHINE_SOUL_CONFIG_DESTINATION:-$HOME/.zshrc}"
exec bash "$root/accumulated_instruments/configuration_deployment/windows/posix_config.sh" "$action" zsh "$source_rel" "$destination" "${1:-prompt}"
