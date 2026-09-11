#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ACTION_ROOT="$SCRIPT_DIR/actions"
MACHINE_SOUL_SETUP="$SCRIPT_DIR/linux/setup-machine-soul.sh"

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

run_machine_soul_setup() {
    printf '\n[Machine Soul] machine-soul-root\n'
    # Source this one so MACHINE_SOUL is also available to the current wrapper.
    # shellcheck source=/dev/null
    source "$MACHINE_SOUL_SETUP"
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

run_all() {
    run_machine_soul_setup
    for action in "${ACTIONS[@]}"; do
        run_action "$action"
    done
}

mapfile -t ACTIONS < <(available_actions)

case "${1:-}" in
    --list)
        printf '%s\n' 'machine-soul-root'
        printf '%s\n' "${ACTIONS[@]}"
        exit 0
        ;;
    --machine-soul)
        run_machine_soul_setup
        exit 0
        ;;
    --all)
        run_all
        exit 0
        ;;
    "") ;;
    *)
        run_action "$1"
        exit $?
        ;;
esac

while true; do
    printf '\nMachine Soul Annexation\n'
    printf '  1. Set up everything available for Linux\n'
    printf '  2. Establish MACHINE_SOUL repository root\n'

    index=3
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
            run_all
            ;;
        2)
            run_machine_soul_setup
            ;;
        *)
            if [[ "$choice" =~ ^[0-9]+$ ]]; then
                action_index=$((choice - 3))
                if (( action_index >= 0 && action_index < ${#ACTIONS[@]} )); then
                    run_action "${ACTIONS[$action_index]}"
                    continue
                fi
            fi

            printf 'Unknown selection.\n' >&2
            ;;
    esac
done
