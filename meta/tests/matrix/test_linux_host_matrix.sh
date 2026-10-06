#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
tmp="$(mktemp -d)"
soul="$tmp/soul"
normal_user="$(id -un)"
apps=(fish bash zsh oh_my_posh contour)
hosts=(fixture_a fixture_b)
accounts=("$normal_user" root)

cleanup() {
    rm -rf -- "$tmp"
}
trap cleanup EXIT

mkdir -p "$soul"
printf 'Machine-Soul repository root\n' > "$soul/.machine_soul_root"

leaf_for() {
    case "$1" in
        fish) printf 'config.fish' ;;
        bash) printf '.bashrc' ;;
        zsh) printf '.zshrc' ;;
        oh_my_posh) printf 'theme.omp.json' ;;
        contour) printf 'contour.yml' ;;
    esac
}

result_code() {
    local wrapper="$1"
    shift
    local output status
    set +e
    output="$(python3 "$wrapper" --json "$@")"
    status=$?
    set -e
    [[ $status -le 3 ]] || return "$status"
    printf '%s' "$output" | python3 -c 'import json,sys; print(json.load(sys.stdin)["code"])'
}

for host in "${hosts[@]}"; do
    for app in "${apps[@]}"; do
        leaf="$(leaf_for "$app")"
        if [[ "$app" == "oh_my_posh" ]]; then
            for account in "${accounts[@]}"; do
                source="$soul/assimilation_directives/$app/hosts/$host/users/$account/$leaf"
                mkdir -p "$(dirname "$source")"
                printf '%s/%s/%s\n' "$host" "$account" "$app" > "$source"
            done
        else
            source="$soul/assimilation_directives/$app/hosts/$host/common/$leaf"
            mkdir -p "$(dirname "$source")"
            printf '%s/common/%s\n' "$host" "$app" > "$source"
        fi
    done
done

export MACHINE_SOUL="$soul"
for host in "${hosts[@]}"; do
    export MACHINE_SOUL_HOST="$host"
    for account in "${accounts[@]}"; do
        for app in "${apps[@]}"; do
            leaf="$(leaf_for "$app")"
            export MACHINE_SOUL_CONFIG_DESTINATION="$tmp/native/$host/$account/$app/config.file"
            mkdir -p "$(dirname "$MACHINE_SOUL_CONFIG_DESTINATION")"
            ops="$repo_root/annexation_procedures/$app"

            [[ "$(result_code "$ops/check_config.py" --account "$account")" == "not_applied" ]]
            [[ "$(result_code "$ops/apply_config.py" --account "$account" --conflict-policy abort)" == "applied" ]]
            [[ "$(result_code "$ops/check_config.py" --account "$account")" == "applied" ]]

            target="$(readlink -- "$MACHINE_SOUL_CONFIG_DESTINATION")"
            if [[ "$app" == "oh_my_posh" ]]; then
                expected="$soul/assimilation_directives/$app/hosts/$host/users/$account/$leaf"
            else
                expected="$soul/assimilation_directives/$app/hosts/$host/common/$leaf"
            fi
            [[ "$target" == "$expected" ]]

            [[ "$(result_code "$ops/unapply_config.py" --account "$account")" == "not_applied" ]]
        done
    done
done

printf 'Linux synthetic host/account/application matrix passed.\n'
