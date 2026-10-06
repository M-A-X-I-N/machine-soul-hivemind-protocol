# Machine-Soul Bash configuration.

if [[ -n "${MACHINE_SOUL:-}" ]] && command -v oh-my-posh >/dev/null 2>&1; then
    _ms_host="$(hostname -s | tr '[:upper:]' '[:lower:]')"
    _ms_user="$(id -un)"
    _ms_user_config="$MACHINE_SOUL/assimilation/oh_my_posh/hosts/$_ms_host/users/$_ms_user/theme.omp.json"
    _ms_common_config="$MACHINE_SOUL/assimilation/oh_my_posh/hosts/$_ms_host/common/theme.omp.json"
    if [[ -f "$_ms_user_config" ]]; then
        eval "$(oh-my-posh init bash --config "$_ms_user_config")"
    elif [[ -f "$_ms_common_config" ]]; then
        eval "$(oh-my-posh init bash --config "$_ms_common_config")"
    fi
    unset _ms_host _ms_user _ms_user_config _ms_common_config
fi
