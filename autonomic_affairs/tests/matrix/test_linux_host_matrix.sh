#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
export MACHINE_SOUL="$repo_root"

tmp="$(mktemp -d)"
cleanup() {
    rm -rf -- "$tmp"
    rm -rf -- "$repo_root/scratch/state/config/workhorse" "$repo_root/scratch/state/config/runar"
    rm -rf -- "$repo_root/scratch/backups/workhorse" "$repo_root/scratch/backups/runar"
}
trap cleanup EXIT

apps=(fish bash zsh oh_my_posh contour)
hosts=(workhorse runar)
accounts=(m-a-x-i-n root)

for host in "${hosts[@]}"; do
    for account in "${accounts[@]}"; do
        export MACHINE_SOUL_HOST="$host"
        export MACHINE_SOUL_ACCOUNT="$account"

        for app in "${apps[@]}"; do
            export MACHINE_SOUL_CONFIG_DESTINATION="$tmp/$host/$account/$app/config.file"
            mkdir -p "$(dirname "$MACHINE_SOUL_CONFIG_DESTINATION")"

            ops="$repo_root/annexation_procedures/$app/linux"
            [[ "$("$ops/check_config.sh")" == "NOT_APPLIED" ]]
            [[ "$("$ops/apply_config.sh" abort)" == "APPLIED" ]]
            [[ "$("$ops/check_config.sh")" == "APPLIED" ]]

            target="$(readlink -- "$MACHINE_SOUL_CONFIG_DESTINATION")"
            if [[ "$app" == "oh_my_posh" ]]; then
                expected="$repo_root/assimilation_directives/oh_my_posh/hosts/$host/users/$account/theme.omp.json"
            else
                case "$app" in
                    fish) leaf="config.fish" ;;
                    bash) leaf=".bashrc" ;;
                    zsh) leaf=".zshrc" ;;
                    contour) leaf="contour.yml" ;;
                esac
                expected="$repo_root/assimilation_directives/$app/hosts/$host/common/$leaf"
            fi

            [[ "$target" == "$expected" ]] || {
                printf 'Matrix mismatch for %s/%s/%s\nexpected: %s\nactual:   %s\n' "$host" "$account" "$app" "$expected" "$target" >&2
                exit 1
            }

            [[ "$("$ops/unapply_config.sh")" == "NOT_APPLIED" ]]
        done
    done
done

printf 'Linux host/account/application matrix passed.\n'
