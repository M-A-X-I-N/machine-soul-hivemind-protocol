#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
tmp="$(mktemp -d)"

cleanup() {
    rm -rf -- "$tmp"
    root_win="$(cygpath -w "$repo_root")"
    MACHINE_SOUL="$root_win" powershell.exe -NoProfile -Command "Remove-Item -LiteralPath '$root_win\\scratch\\state\\config\\spaceship' -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -LiteralPath '$root_win\\scratch\\backups\\spaceship' -Recurse -Force -ErrorAction SilentlyContinue" >/dev/null 2>&1 || true
}
trap cleanup EXIT

export MACHINE_SOUL="$repo_root"
export MACHINE_SOUL_HOST="spaceship"
export MACHINE_SOUL_ACCOUNT="ci-posix"

for app in fish bash zsh; do
    export MACHINE_SOUL_CONFIG_DESTINATION="$tmp/$app/config.file"
    mkdir -p "$(dirname "$MACHINE_SOUL_CONFIG_DESTINATION")"
    ops="$repo_root/annexation_procedures/$app/windows"

    [[ "$("$ops/check_config.sh")" == "NOT_APPLIED" ]]
    [[ "$("$ops/apply_config.sh" abort)" == "APPLIED" ]]
    [[ "$("$ops/check_config.sh")" == "APPLIED" ]]
    [[ "$("$ops/apply_config.sh" abort)" == "APPLIED" ]]

    target="$(readlink "$MACHINE_SOUL_CONFIG_DESTINATION" 2>/dev/null || true)"
    # Git Bash may not understand a Windows-native symlink as a POSIX symlink.
    # PowerShell Check above is the ownership/state authority; verify content too.
    [[ -s "$MACHINE_SOUL_CONFIG_DESTINATION" ]]

    [[ "$("$ops/unapply_config.sh")" == "NOT_APPLIED" ]]
    [[ "$("$ops/check_config.sh")" == "NOT_APPLIED" ]]
done

printf 'Windows POSIX-shell config adapter tests passed.\n'
