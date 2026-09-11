#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ACTION_ROOT="$SCRIPT_DIR/actions"

available_actions() {
    [[ -d "$ACTION_ROOT" ]] || return 0

    find "$ACTION_ROOT" -mindepth 1 -maxdepth 1 -type d -print0 \
        | while IFS= read -r -d '' dir; do
            if [[ -f "$dir/setup.sh" ]]; then
                basename "$dir"
            fi
        done \
        | sort
}

run_action() {
    local name="$1"
    local script="$ACTION_ROOT/$name/setup.sh"

    if [[ ! -f "$script" ]]; then
        printf "No Linux setup action named '%s' was discovered.\n" "$name" >&2
        return 1
    fi

    printf '\n[Machine Soul] %s\n' "$name"
    bash "$script"
}

mapfile -t ACTIONS < <(available_actions)

case "${1:-}" in
    --list)
        printf '%s\n' "${ACTIONS[@]}"
        exit 0
        ;;
    --all)
        for action in "${ACTIONS[@]}"; do
            run_action "$action"
        done
        exit 0
        ;;
    "") ;;
    *)
        run_action "$1"
        exit $?
        ;;
esac

if (( ${#ACTIONS[@]} == 0 )); then
    printf '[Machine Soul] No Linux setup actions were discovered.\n'
    exit 0
fi

while true; do
    printf '\nMachine Soul Annexation\n'
    printf '  1. Set up everything available for Linux\n'

    index=2
    for action in "${ACTIONS[@]}"; do
        printf '  %d. %s\n' "$index" "$action"
        ((index++))
    done

    printf '  Q. Quit\n'
    read -r -p 'Select action: ' choice

    case "${choice,,}" in
        q)
            exit 0
            ;;
        1)
            for action in "${ACTIONS[@]}"; do
                run_action "$action"
            done
            ;;
        *)
            if [[ "$choice" =~ ^[0-9]+$ ]]; then
                action_index=$((choice - 2))
                if (( action_index >= 0 && action_index < ${#ACTIONS[@]} )); then
                    run_action "${ACTIONS[$action_index]}"
                    continue
                fi
            fi

            printf 'Unknown selection.\n' >&2
            ;;
    esac
done
