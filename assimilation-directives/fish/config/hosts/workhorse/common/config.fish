# Machine-Soul Fish configuration.

if set -q MACHINE_SOUL; and type -q oh-my-posh
    set -l ms_host (hostname -s | string lower)
    set -l ms_user (id -un)
    set -l user_config "$MACHINE_SOUL/assimilation-directives/oh-my-posh/config/hosts/$ms_host/users/$ms_user/theme.omp.json"
    set -l common_config "$MACHINE_SOUL/assimilation-directives/oh-my-posh/config/hosts/$ms_host/common/theme.omp.json"

    if test -f "$user_config"
        oh-my-posh init fish --config "$user_config" | source
    else if test -f "$common_config"
        oh-my-posh init fish --config "$common_config" | source
    end
end
