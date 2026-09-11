#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MACHINE_SOUL_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PROFILE_FILE="$HOME/.profile"
START_MARKER='# >>> MACHINE_SOUL >>>'
END_MARKER='# <<< MACHINE_SOUL <<<'

export MACHINE_SOUL="$MACHINE_SOUL_ROOT"

mkdir -p "$(dirname -- "$PROFILE_FILE")"
touch "$PROFILE_FILE"

TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

awk -v start="$START_MARKER" -v end="$END_MARKER" '
    $0 == start { skip=1; next }
    $0 == end   { skip=0; next }
    !skip       { print }
' "$PROFILE_FILE" > "$TMP_FILE"

{
    cat "$TMP_FILE"
    printf '\n%s\n' "$START_MARKER"
    printf 'export MACHINE_SOUL=%q\n' "$MACHINE_SOUL_ROOT"
    printf '%s\n' "$END_MARKER"
} > "$PROFILE_FILE"

printf '[Machine Soul] MACHINE_SOUL -> %s\n' "$MACHINE_SOUL_ROOT"
printf '[Machine Soul] Persisted in %s\n' "$PROFILE_FILE"
