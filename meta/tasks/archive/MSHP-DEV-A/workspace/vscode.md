# VS Code annexation investigation

Status: completed research output for `MSHP-DEV-A-010`.

Research date: 2026-09-28.

## Installation

Official VS Code Windows documentation exposes distinct User setup, System setup, and ZIP distributions.

- User setup is the recommended ordinary Windows install, requires no admin, and installs under `%LOCALAPPDATA%\Programs\Microsoft VS Code`.
- System setup installs for all users under Program Files and requires elevation.
- ZIP is a portable/manual-update distribution.

Current WinGet package identity: `Microsoft.VisualStudioCode`.

The current WinGet manifest inspected during this task (`1.125.1`) exposes both `Scope: user` and `Scope: machine` installers for x64 and arm64. This maps directly onto the scoped WinGet machinery already implemented by Machine-Soul.

Sources:
- https://code.visualstudio.com/docs/setup/windows
- https://github.com/microsoft/winget-pkgs/blob/master/manifests/m/Microsoft/VisualStudioCode/1.125.1/Microsoft.VisualStudioCode.installer.yaml

Initial recommendation: if/when VS Code installation is promoted, prefer an explicit required USER scope unless the maintainer chooses otherwise. Machine-scope remains representable.

## Base user configuration

Official VS Code settings documentation gives the Windows base user settings path:

`%APPDATA%\Code\User\settings.json`

User keyboard customizations live in `keybindings.json`, and user snippets are JSON/`.code-snippets` content under the user snippet area.

Sources:
- https://code.visualstudio.com/docs/configure/settings
- https://code.visualstudio.com/docs/configure/keybindings
- https://code.visualstudio.com/docs/editing/userdefinedsnippets

These are strong assimilation-directive candidates when canonical desired content is supplied.

Workspace `.vscode` settings/snippets belong with the project repository, not Machine-Soul global assimilation, unless a future explicit cross-project policy says otherwise.

## Profiles

VS Code Profiles are not merely a second settings file. A profile can include/substitute:

- settings;
- keyboard shortcuts;
- snippets;
- tasks;
- extensions;
- UI layout/state;
- MCP servers and newer customization categories.

Profiles are stored under `%APPDATA%\Code\User\profiles` and can be exported/imported as `.code-profile` files. The CLI can select a profile with `--profile`; extension CLI operations also accept `--profile`.

Source: https://code.visualstudio.com/docs/configure/profiles

Recommendation: do not symlink the entire `profiles/` state tree. Treat profile export/import or a future declarative profile adapter as a separate capability from base user files. Profile IDs/folder associations/UI state are not automatically canonical Machine-Soul config.

## Extensions

The `code` CLI provides stable machine-readable extension operations:

- `--list-extensions`;
- `--show-versions`;
- `--install-extension <publisher.id[@version]>`;
- `--uninstall-extension <publisher.id>`;
- profile-specific extension operations with `--profile`.

Sources:
- https://code.visualstudio.com/docs/configure/command-line
- https://code.visualstudio.com/docs/configure/extensions/extension-marketplace

Extensions execute with VS Code's permissions and are package-like executable state, not ordinary configuration files.

Recommendation: model extension inventory as a distinct annexation capability/plugin-package domain if the comparative JetBrains work supports a reusable concept. Do not encode extensions inside `settings.json` or assimilate the extension directory wholesale.

## Settings Sync ownership

VS Code Settings Sync can synchronize settings, keyboard shortcuts, snippets, user tasks, UI state, extensions, profiles, prompts/instructions, and related categories. It deliberately excludes machine/machine-overridable settings and supports ignored settings/extensions.

Source: https://code.visualstudio.com/docs/configure/settings-sync

This creates overlapping ownership with Machine-Soul.

Safe rule:

> For each synchronized category, choose an owner. Machine-Soul must not silently fight Settings Sync over the same desired state.

Possible future modes include:

- Machine-Soul owns a category and Settings Sync excludes it;
- Settings Sync owns a category and Machine-Soul only observes/ignores it;
- Machine-Soul manages installation only and leaves all editor-state sync to VS Code;
- profile/export integration that intentionally cooperates with Sync.

The investigation does not choose among these without maintainer preference.

## Portable mode

Portable mode stores both user data and extensions under a `data` directory beside a ZIP distribution. That is a distinct deployment model and should not be conflated with the standard installed-user configuration paths.

Source: https://code.visualstudio.com/docs/setup/portable

Machine-Soul need not support portable mode in the first implementation unless explicitly desired.

## State to exclude

Do not assimilate the entire VS Code user-data tree. Exclude or separately reason about:

- authentication/session state;
- Settings Sync credentials/account state;
- workspace history/recent items;
- caches/logs;
- machine IDs and telemetry state;
- extension binaries/directories;
- remote SSH/WSL/container extension state;
- temporary/ephemeral profiles;
- generated UI/session state unless deliberately owned.

## Capability recommendation

Potential near-term annexation capabilities:

1. **Install/Uninstall/CheckInstalled** through scoped WinGet.
2. **Base user settings/keybindings/snippets** through ordinary assimilation directives once desired content is supplied.
3. **Extensions** through a distinct CLI-backed inventory capability, pending cross-IDE synthesis.
4. **Profiles** through a separate profile/export model, pending maintainer desired usage.
5. **Settings Sync coexistence policy** before Machine-Soul claims any category already synchronized.

Install support does not depend on configuration support.

## Promotion readiness

Installation support is technically promotable now because package identity/scope are known and no canonical config is required.

Configuration, extension inventory, profile state, and Sync ownership require maintainer preference/desired state or comparative synthesis before implementation.
