# MSHP-WIN-CONFIG — Additional Windows configuration surfaces

**Status:** OPEN

## Goal

Expand Machine-Soul's Windows desired-state coverage only where Windows applications/platform tools expose stable, supportable configuration contracts.

## Current state / coverage

Already managed baseline applications include Windows Terminal, PowerShell, CMD, Oh My Posh, Contour, and Windows POSIX-shell configs.

`MSHP-APPS-A-010` identified three strong ordinary file-config candidates that are technically ready once canonical desired content is chosen:

- WinGet client user `settings.json`;
- WSL global `%UserProfile%\.wslconfig`;
- Windows OpenSSH client `%UserProfile%\.ssh\config`.

The installation-scope block is complete for current WinGet/Apt mutation, so managed WinGet client scope preferences cannot silently change Machine-Soul-controlled install scope.

## Known gaps

- canonical desired WinGet settings have not yet been selected/imported;
- canonical desired `.wslconfig` has not yet been selected/imported;
- canonical desired OpenSSH client host/options have not yet been selected/imported;
- PowerToys desired modules/settings have not been selected and require a native DSC configuration strategy;
- Windows Sandbox `.wsb` profiles need a profile/asset model rather than ordinary singleton Apply;
- Windows Explorer/Advanced Settings belong to a future Windows OS-state/registry-policy domain;
- Notepad has no supported ordinary user-settings contract suitable for management at present.

## Deliberate boundaries / deferred work

- Do not invent maintainer preferences to make an application integration executable.
- Do not replace existing unmanaged WinGet/WSL/SSH config with empty/default tracked files.
- Do not track SSH keys, known_hosts, credentials, tokens, or generated/session state.
- Keep WinGet user settings separate from administrator settings, sources, and WinGet Configuration/DSC.
- Prefer PowerToys' supported DSC interface over symlinking internal module JSON files.
- Treat Sandbox profiles as assets/launch profiles, not as one singleton application config.
- Treat Explorer/Advanced Settings as Windows OS state rather than an app config entry.
- Windhawk remains separately tracked in reminders.

## Related executable tasks

`MSHP-APPS-A-010` completed the research/classification. No implementation task is currently promoted because the strong candidates require maintainer-selected canonical desired state first.

Task state remains authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

Promote WinGet, WSL, or OpenSSH into bounded application-integration tasks when the maintainer supplies/approves the canonical desired config content or explicitly authorizes capturing existing config as the canonical source.

Promote PowerToys when desired module state is available and the native DSC adapter boundary is approved.

This initiative can become COMPLETE when all Windows configuration surfaces the maintainer actually wants managed are either implemented or explicitly rejected/deferred outside the desired support surface.
