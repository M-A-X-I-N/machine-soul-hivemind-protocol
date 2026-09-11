#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

run_action() {
    local name="$1"
    case "$name" in
        machine-soul-root)
            printf '\n[Machine Soul] Establish MACHINE_SOUL repository root\n'
            "$SCRIPT_DIR/machine-soul-root/setup.sh"
            ;;
        contour)
            printf '\n[Machine Soul] Enable Contour configuration\n'
            "$SCRIPT_DIR/contour/setup.sh"
            ;;
        *)
            printf 'Unknown setup action: %s\n' "$name" >&2
            return 1
            ;;
    esac
}

run_all() {
    run_action machine-soul-root
    run_action contour
}

case "${1:-}" in
    --all)
        run_all
        exit 0
        ;;
    machine-soul-root|contour)
        run_action "$1"
        exit 0
        ;;
    "") ;;
    *)
        printf 'Usage: %s [--all|machine-soul-root|contour]\n' "$0" >&2
        exit 2
        ;;
esac

while true; do
    printf '\nMachine Soul Annexation\n'
    printf '  1. Set up everything for current OS\n'
    printf '  2. Establish MACHINE_SOUL repository root\n'
    printf '  3. Enable Contour configuration\n'
    printf '  Q. Quit\n'
    read -r -p 'Select action: ' choice

    case "${choice,,}" in
        1) run_all ;;
        2) run_action machine-soul-root ;;
        3) run_action contour ;;
        q) exit 0 ;;
        *) printf 'Unknown selection.\n' >&2 ;;
    esac
done
