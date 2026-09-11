#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MACHINE_SOUL_ROOT="${MACHINE_SOUL:-$(cd -- "$SCRIPT_DIR/../.." && pwd)}"

if ! command -v contour >/dev/null 2>&1; then
    printf '[Machine Soul] Contour not found; skipping.\n'
    exit 0
fi

SOURCE="$MACHINE_SOUL_ROOT/assimilation-directives/contour/contour.yml"
TARGET_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/contour"
TARGET="$TARGET_DIR/contour.yml"

if [[ ! -f "$SOURCE" ]]; then
    printf 'Canonical Contour config missing: %s\n' "$SOURCE" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

if [[ -L "$TARGET" ]]; then
    current="$(readlink -f -- "$TARGET" 2>/dev/null || true)"
    source_real="$(readlink -f -- "$SOURCE")"
    if [[ "$current" == "$source_real" ]]; then
        printf '[Machine Soul] Contour config already enabled.\n'
        exit 0
    fi
fi

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    backup="$TARGET.pre-machine-soul-$(date +%Y%m%d-%H%M%S)"
    mv -- "$TARGET" "$backup"
    printf '[Machine Soul] Preserved existing Contour config: %s\n' "$backup"
fi

ln -s "$SOURCE" "$TARGET"
printf '[Machine Soul] Contour config -> %s\n' "$SOURCE"
