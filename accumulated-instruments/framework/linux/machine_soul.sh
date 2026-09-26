#!/usr/bin/env bash

# Shared Machine-Soul runtime for Ubuntu/Linux.
# This file is intended to be sourced from application operation scripts.

ms_die() {
    printf 'ERROR: %s\n' "$*" >&2
    return 3
}

ms_root() {
    if [[ -n "${MACHINE_SOUL:-}" ]]; then
        if [[ -f "$MACHINE_SOUL/TASKS.md" ]]; then
            printf '%s\n' "$(cd "$MACHINE_SOUL" && pwd -P)"
            return 0
        fi
        ms_die "MACHINE_SOUL points to '$MACHINE_SOUL', but TASKS.md was not found there."
        return $?
    fi

    local cursor
    cursor="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
    while [[ "$cursor" != "/" ]]; do
        if [[ -f "$cursor/TASKS.md" && -f "$cursor/AGENTS.md" ]]; then
            export MACHINE_SOUL="$cursor"
            printf '%s\n' "$cursor"
            return 0
        fi
        cursor="$(dirname "$cursor")"
    done

    ms_die "Unable to resolve MACHINE_SOUL from environment or repository ancestry."
}

ms_host() {
    if [[ -n "${MACHINE_SOUL_HOST:-}" ]]; then
        printf '%s\n' "${MACHINE_SOUL_HOST,,}"
    else
        hostname -s | tr '[:upper:]' '[:lower:]'
    fi
}

ms_account() {
    if [[ -n "${MACHINE_SOUL_ACCOUNT:-}" ]]; then
        printf '%s\n' "$MACHINE_SOUL_ACCOUNT"
    else
        id -un
    fi
}

ms_scratch_path() {
    local relative="$1"
    local create="${2:-false}"
    local root
    root="$(ms_root)" || return $?
    local path="$root/scratch/$relative"
    if [[ "$create" == "true" ]]; then
        mkdir -p -- "$path" || return 3
    fi
    printf '%s\n' "$path"
}

ms_abs_path_no_follow() {
    local input="$1"
    local parent base
    parent="$(dirname "$input")"
    base="$(basename "$input")"
    parent="$(realpath -m -- "$parent")" || return 3
    printf '%s/%s\n' "$parent" "$base"
}

ms_path_hash() {
    local path
    path="$(ms_abs_path_no_follow "$1")" || return $?
    printf '%s' "$path" | sha256sum | awk '{print $1}'
}

ms_resolve_link_target() {
    local destination="$1"
    local raw_target="$2"
    if [[ "$raw_target" = /* ]]; then
        realpath -m -- "$raw_target"
    else
        realpath -m -- "$(dirname "$destination")/$raw_target"
    fi
}

ms_link_info() {
    local source destination expected raw actual
    source="$(realpath -m -- "$1")"
    destination="$(ms_abs_path_no_follow "$2")" || return $?
    expected="$source"

    if [[ -L "$destination" ]]; then
        raw="$(readlink -- "$destination")" || return 3
        actual="$(ms_resolve_link_target "$destination" "$raw")" || return 3

        if [[ "$actual" == "$expected" && -f "$actual" ]]; then
            printf 'APPLIED\t%s\t%s\n' "$expected" "$actual"
        elif [[ ! -e "$actual" ]]; then
            printf 'BROKEN\t%s\t%s\n' "$expected" "$actual"
        else
            printf 'WRONG_TARGET\t%s\t%s\n' "$expected" "$actual"
        fi
        return 0
    fi

    if [[ -e "$destination" ]]; then
        printf 'CONFLICT\t%s\t\n' "$expected"
        return 0
    fi

    printf 'NOT_APPLIED\t%s\t\n' "$expected"
}

ms_config_state() {
    local line
    line="$(ms_link_info "$1" "$2")" || return $?
    printf '%s\n' "${line%%$'\t'*}"
}

ms_link_points_to_expected() {
    local source destination raw actual expected
    source="$(realpath -m -- "$1")"
    destination="$(ms_abs_path_no_follow "$2")" || return $?
    [[ -L "$destination" ]] || return 1
    raw="$(readlink -- "$destination")" || return 1
    actual="$(ms_resolve_link_target "$destination" "$raw")" || return 1
    expected="$source"
    [[ "$actual" == "$expected" ]]
}

ms_b64_encode() {
    printf '%s' "$1" | base64 | tr -d '\n'
}

ms_b64_decode() {
    printf '%s' "$1" | base64 -d
}

ms_state_path() {
    local application="$1"
    local destination="$2"
    local host account hash dir
    host="$(ms_host)"
    account="$(ms_account)"
    hash="$(ms_path_hash "$destination")"
    dir="$(ms_scratch_path "state/config/$host/$account/$application" true)" || return $?
    printf '%s/%s.state\n' "$dir" "$hash"
}

ms_write_state() {
    local path="$1"
    local application="$2"
    local source="$3"
    local destination="$4"
    local prior_type="$5"
    local backup="$6"
    local prior_target="$7"
    local root temp backup_relative
    root="$(ms_root)" || return $?
    temp="$path.tmp-$"
    backup_relative=""
    if [[ -n "$backup" && "$backup" == "$root/"* ]]; then
        backup_relative="${backup#"$root"/}"
    fi

    {
        printf 'schema=2\n'
        printf 'application_b64=%s\n' "$(ms_b64_encode "$application")"
        printf 'host_b64=%s\n' "$(ms_b64_encode "$(ms_host)")"
        printf 'account_b64=%s\n' "$(ms_b64_encode "$(ms_account)")"
        printf 'source_relative_b64=%s\n' "$(ms_b64_encode "${source#"$root"/}")"
        printf 'destination_b64=%s\n' "$(ms_b64_encode "$destination")"
        printf 'prior_type=%s\n' "$prior_type"
        printf 'backup_relative_b64=%s\n' "$(ms_b64_encode "$backup_relative")"
        printf 'backup_b64=%s\n' "$(ms_b64_encode "$backup")"
        printf 'prior_target_b64=%s\n' "$(ms_b64_encode "$prior_target")"
        printf 'applied_target_b64=%s\n' "$(ms_b64_encode "$source")"
        printf 'applied_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$temp" || return 3

    mv -- "$temp" "$path" || return 3
}

ms_read_state_field() {
    local path="$1"
    local wanted="$2"
    local line key value
    [[ -f "$path" ]] || return 1
    while IFS= read -r line; do
        key="${line%%=*}"
        value="${line#*=}"
        if [[ "$key" == "$wanted" ]]; then
            printf '%s\n' "$value"
            return 0
        fi
    done < "$path"
    return 1
}

ms_apply_file() {
    local application="$1"
    local source="$2"
    local destination="$3"
    local policy="${4:-prompt}"

    source="$(realpath -m -- "$source")"
    destination="$(ms_abs_path_no_follow "$destination")" || return $?

    [[ -f "$source" ]] || { ms_die "Canonical source file does not exist: $source"; return $?; }

    local status
    status="$(ms_config_state "$source" "$destination")" || return $?

    if [[ "$status" == "APPLIED" ]]; then
        printf 'APPLIED\n'
        return 0
    fi

    # A moved MACHINE_SOUL checkout changes the concrete symlink target.
    # If deployment state proves the current stale link is the one we previously
    # created, repair it in place while preserving the original pre-managed state.
    if [[ ( "$status" == "WRONG_TARGET" || "$status" == "BROKEN" ) && -L "$destination" ]]; then
        local relocation_state old_target_b64 old_target source_rel_b64 source_rel
        local saved_prior_type saved_backup_relative_b64 saved_backup_relative saved_backup_b64 saved_backup saved_prior_target_b64 saved_prior_target
        relocation_state="$(ms_state_path "$application" "$destination")" || return $?
        if [[ -f "$relocation_state" ]]; then
            old_target_b64="$(ms_read_state_field "$relocation_state" applied_target_b64 2>/dev/null || true)"
            source_rel_b64="$(ms_read_state_field "$relocation_state" source_relative_b64 2>/dev/null || true)"
            old_target=""
            source_rel=""
            [[ -n "$old_target_b64" ]] && old_target="$(ms_b64_decode "$old_target_b64")"
            [[ -n "$source_rel_b64" ]] && source_rel="$(ms_b64_decode "$source_rel_b64")"

            local raw_current current_target current_root
            raw_current="$(readlink -- "$destination")" || return 3
            current_target="$(ms_resolve_link_target "$destination" "$raw_current")" || return 3
            current_root="$(ms_root)" || return $?

            if [[ -n "$old_target" && "$current_target" == "$old_target" && "$current_root/$source_rel" == "$source" ]]; then
                saved_prior_type="$(ms_read_state_field "$relocation_state" prior_type 2>/dev/null || true)"
                saved_backup_relative_b64="$(ms_read_state_field "$relocation_state" backup_relative_b64 2>/dev/null || true)"
                saved_backup_b64="$(ms_read_state_field "$relocation_state" backup_b64 2>/dev/null || true)"
                saved_prior_target_b64="$(ms_read_state_field "$relocation_state" prior_target_b64 2>/dev/null || true)"
                saved_backup_relative=""
                saved_backup=""
                saved_prior_target=""
                [[ -n "$saved_backup_relative_b64" ]] && saved_backup_relative="$(ms_b64_decode "$saved_backup_relative_b64")"
                if [[ -n "$saved_backup_relative" ]]; then
                    saved_backup="$current_root/$saved_backup_relative"
                elif [[ -n "$saved_backup_b64" ]]; then
                    saved_backup="$(ms_b64_decode "$saved_backup_b64")"
                fi
                [[ -n "$saved_prior_target_b64" ]] && saved_prior_target="$(ms_b64_decode "$saved_prior_target_b64")"

                rm -- "$destination" || return 3
                if ! ln -s -- "$source" "$destination"; then
                    ln -s -- "$raw_current" "$destination" || true
                    ms_die "Failed to repair relocated managed symlink: $destination"
                    return $?
                fi

                if [[ "$(ms_config_state "$source" "$destination")" != "APPLIED" ]]; then
                    rm -- "$destination" || true
                    ln -s -- "$raw_current" "$destination" || true
                    ms_die "Relocated symlink repair verification failed: $destination"
                    return $?
                fi

                ms_write_state "$relocation_state" "$application" "$source" "$destination" "$saved_prior_type" "$saved_backup" "$saved_prior_target" || return $?
                printf 'APPLIED\n'
                return 0
            fi
        fi
    fi

    local prior_type="absent"
    local prior_target=""
    local backup=""

    if [[ "$status" != "NOT_APPLIED" ]]; then
        if [[ -d "$destination" && ! -L "$destination" ]]; then
            ms_die "Destination is a directory and cannot be replaced as a managed config file: $destination"
            return $?
        fi

        case "$policy" in
            abort)
                printf 'CONFLICT\n'
                return 1
                ;;
            prompt)
                printf "Existing unmanaged configuration detected at '%s'. Preserve and replace it? [y/N] " "$destination" >&2
                local answer
                IFS= read -r answer
                case "${answer,,}" in
                    y|yes) ;;
                    *) printf 'CONFLICT\n'; return 1 ;;
                esac
                ;;
            backup-and-replace) ;;
            *)
                ms_die "Unknown conflict policy: $policy"
                return $?
                ;;
        esac

        if [[ -L "$destination" ]]; then
            prior_type="symlink"
            prior_target="$(readlink -- "$destination")" || return 3
            rm -- "$destination" || return 3
        else
            prior_type="file"
            local host account hash stamp backup_dir
            host="$(ms_host)"
            account="$(ms_account)"
            hash="$(ms_path_hash "$destination")"
            stamp="$(date -u +%Y%m%dT%H%M%S%NZ)"
            backup_dir="$(ms_scratch_path "backups/$host/$account/$application/$stamp-$hash" true)" || return $?
            backup="$backup_dir/original"
            mv -- "$destination" "$backup" || return 3
        fi
    fi

    mkdir -p -- "$(dirname "$destination")" || return 3

    if ! ln -s -- "$source" "$destination"; then
        if [[ -L "$destination" ]]; then
            rm -- "$destination" || true
        fi
        if [[ "$prior_type" == "file" && -f "$backup" ]]; then
            mv -- "$backup" "$destination" || true
        elif [[ "$prior_type" == "symlink" ]]; then
            ln -s -- "$prior_target" "$destination" || true
        fi
        ms_die "Failed to create managed symlink: $destination"
        return $?
    fi

    if [[ "$(ms_config_state "$source" "$destination")" != "APPLIED" ]]; then
        rm -- "$destination" || true
        if [[ "$prior_type" == "file" && -f "$backup" ]]; then
            mv -- "$backup" "$destination" || true
        elif [[ "$prior_type" == "symlink" ]]; then
            ln -s -- "$prior_target" "$destination" || true
        fi
        ms_die "Symlink verification failed for: $destination"
        return $?
    fi

    local state_path
    state_path="$(ms_state_path "$application" "$destination")" || return $?
    ms_write_state "$state_path" "$application" "$source" "$destination" "$prior_type" "$backup" "$prior_target" || return $?

    printf 'APPLIED\n'
}

ms_unapply_file() {
    local application="$1"
    local source="$2"
    local destination="$3"

    source="$(realpath -m -- "$source")"
    destination="$(ms_abs_path_no_follow "$destination")" || return $?

    if [[ ! -e "$destination" && ! -L "$destination" ]]; then
        printf 'NOT_APPLIED\n'
        return 0
    fi

    if ! ms_link_points_to_expected "$source" "$destination"; then
        printf 'CONFLICT\n'
        return 1
    fi

    local state_path prior_type backup_relative_b64 backup_relative backup_b64 prior_target_b64 backup prior_target root
    state_path="$(ms_state_path "$application" "$destination")" || return $?
    prior_type="$(ms_read_state_field "$state_path" prior_type 2>/dev/null || true)"
    backup_relative_b64="$(ms_read_state_field "$state_path" backup_relative_b64 2>/dev/null || true)"
    backup_b64="$(ms_read_state_field "$state_path" backup_b64 2>/dev/null || true)"
    prior_target_b64="$(ms_read_state_field "$state_path" prior_target_b64 2>/dev/null || true)"
    backup_relative=""
    backup=""
    prior_target=""
    root="$(ms_root)" || return $?
    [[ -n "$backup_relative_b64" ]] && backup_relative="$(ms_b64_decode "$backup_relative_b64")"
    if [[ -n "$backup_relative" ]]; then
        backup="$root/$backup_relative"
    elif [[ -n "$backup_b64" ]]; then
        backup="$(ms_b64_decode "$backup_b64")"
    fi
    [[ -n "$prior_target_b64" ]] && prior_target="$(ms_b64_decode "$prior_target_b64")"

    rm -- "$destination" || return 3

    case "$prior_type" in
        file)
            if [[ -f "$backup" ]]; then
                mv -- "$backup" "$destination" || {
                    ms_die "Managed link removed but backup restoration failed: $backup"
                    return $?
                }
            else
                ms_die "Managed link removed but recorded backup is missing: $backup"
                return $?
            fi
            ;;
        symlink)
            if [[ -n "$prior_target" ]]; then
                ln -s -- "$prior_target" "$destination" || return 3
            fi
            ;;
        absent|"") ;;
        *)
            ms_die "Unknown prior_type in deployment state: $prior_type"
            return $?
            ;;
    esac

    [[ -f "$state_path" ]] && rm -- "$state_path"
    printf 'NOT_APPLIED\n'
}
