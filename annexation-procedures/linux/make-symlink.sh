#!/usr/bin/env bash
set -euo pipefail

if (( $# != 2 )); then
    printf 'Usage: %s <source> <target>\n' "$0" >&2
    exit 2
fi

SOURCE="$1"
TARGET="$2"
SOURCE_REAL="$(readlink -f -- "$SOURCE")"
TARGET_DIR="$(dirname -- "$TARGET")"

mkdir -p "$TARGET_DIR"

if [[ -L "$TARGET" ]]; then
    CURRENT="$(readlink -f -- "$TARGET" 2>/dev/null || true)"
    if [[ "$CURRENT" == "$SOURCE_REAL" ]]; then
        printf '[Machine Soul] Symlink already correct: %s -> %s\n' "$TARGET" "$SOURCE_REAL"
        exit 0
    fi
fi

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    BACKUP="$TARGET.pre-machine-soul-$(date +%Y%m%d-%H%M%S)"
    mv -- "$TARGET" "$BACKUP"
    printf '[Machine Soul] Preserved existing target: %s\n' "$BACKUP"
fi

ln -s "$SOURCE_REAL" "$TARGET"
printf '[Machine Soul] Linked: %s -> %s\n' "$TARGET" "$SOURCE_REAL"
