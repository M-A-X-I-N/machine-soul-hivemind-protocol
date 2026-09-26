#!/usr/bin/env bash
set -euo pipefail
action="$(basename "$0" .sh)"
case "$action" in
    apply_config) action=apply ;;
    unapply_config) action=unapply ;;
    check_config) action=check ;;
    *) printf 'ERROR: unsupported operation entry point: %s\n' "$action" >&2; exit 3 ;;
esac
exec "$(dirname "$0")/manage_config.sh" "$action" "$@"
