#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MACHINE_SOUL_ROOT="${MACHINE_SOUL:-$(cd -- "$SCRIPT_DIR/../../.." && pwd)}"

if ! command -v contour >/dev/null 2>&1; then
    printf '[Machine Soul] Contour not found; skipping.\n'
    exit 0
fi

SOURCE="$MACHINE_SOUL_ROOT/assimilation-directives/contour/contour.yml"
TARGET="${XDG_CONFIG_HOME:-$HOME/.config}/contour/contour.yml"
SYMLINK_HELPER="$MACHINE_SOUL_ROOT/annexation-procedures/linux/make-symlink.sh"

if [[ ! -f "$SOURCE" ]]; then
    printf 'Canonical Contour config missing: %s\n' "$SOURCE" >&2
    exit 1
fi

bash "$SYMLINK_HELPER" "$SOURCE" "$TARGET"
