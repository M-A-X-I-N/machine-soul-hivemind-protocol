# VS Code annexation findings

Durable findings from `MSHP-DEV-A-010` (2026-09-28):

- `Microsoft.VisualStudioCode` currently exposes both WinGet USER and MACHINE installers; user setup is Microsoft's recommended normal install.
- Base user `settings.json` is `%APPDATA%\Code\User\settings.json`; keybindings and snippets are independent assimilatable user state.
- Profiles are composite state (settings/extensions/snippets/tasks/UI/etc.) with `.code-profile` export/import and should not be treated as a raw directory symlink by default.
- VS Code CLI provides stable profile-aware extension list/install/uninstall operations; extensions are executable package state, not config files.
- Settings Sync overlaps Machine-Soul ownership across settings, shortcuts, snippets, tasks, UI, extensions, profiles, and newer customization categories. Choose one owner per category; do not silently fight Sync.
- Installation-only annexation is independently useful and does not require assimilation directives.

Detailed research lives in `autonomic_affairs/tasks/archive/MSHP-DEV-A/workspace/vscode.md`.