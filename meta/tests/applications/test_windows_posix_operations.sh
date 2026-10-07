#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp="$(mktemp -d)"
original_home="${HOME:-}"

cleanup() {
    export HOME="$original_home"
    rm -rf -- "$tmp"
    root_win="$(cygpath -w "$repo_root")"
    powershell.exe -NoProfile -Command "Remove-Item -LiteralPath '$root_win\\scratch\\state\\config\\spaceship' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath '$root_win\\scratch\\backups\\spaceship' -Recurse -Force -ErrorAction SilentlyContinue" >/dev/null 2>&1 || true
}
trap cleanup EXIT

export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="spaceship"
unset MACHINE_SOUL_ACCOUNT || true
unset MACHINE_SOUL_CONFIG_DESTINATION || true
export HOME="$tmp/home"
mkdir -p "$HOME"

result_code() {
    local wrapper="$1"
    shift
    local output status
    set +e
    output="$(python "$wrapper" --json "$@")"
    status=$?
    set -e
    [[ $status -le 3 ]] || return "$status"
    printf '%s' "$output" | python -c 'import json,sys; print(json.load(sys.stdin)["code"])'
}

for app in fish bash zsh; do
    ops="$repo_root/annexation/$app"

    [[ "$(result_code "$ops/check_config.py")" == "not_applied" ]]
    [[ "$(result_code "$ops/apply_config.py" --conflict-policy abort)" == "applied" ]]
    [[ "$(result_code "$ops/check_config.py")" == "applied" ]]
    [[ "$(result_code "$ops/apply_config.py" --conflict-policy abort)" == "applied" ]]

    case "$app" in
        fish) destination="$HOME/.config/fish/config.fish" ;;
        bash) destination="$HOME/.bashrc" ;;
        zsh) destination="$HOME/.zshrc" ;;
    esac
    [[ -s "$destination" ]]

    [[ "$(result_code "$ops/unapply_config.py")" == "not_applied" ]]
    [[ "$(result_code "$ops/check_config.py")" == "not_applied" ]]
done

printf 'Windows POSIX Python-wrapper operation tests passed.\n'
