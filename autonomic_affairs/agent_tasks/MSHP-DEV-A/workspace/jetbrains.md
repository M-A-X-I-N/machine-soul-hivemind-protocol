# JetBrains / Toolbox annexation investigation

Status: completed research output for `MSHP-DEV-A-020`.

Research date: 2026-09-28.

## Toolbox installation

Current WinGet identity: `JetBrains.Toolbox`.

The current community manifest inspected during this task is `3.8.1.0` (release date 2026-09-17) and declares `Scope: user` for x64 and arm64 installers.

Source:
- https://github.com/microsoft/winget-pkgs/blob/master/manifests/j/JetBrains/Toolbox/3.8.1.0/JetBrains.Toolbox.installer.yaml

JetBrains also documents silent Toolbox installation on Windows starting with Toolbox 2.4.

Source: https://www.jetbrains.com/help/toolbox-app/installation.html

Recommendation: Toolbox itself is technically ready for Machine-Soul scoped WinGet installation as a USER-scoped subject.

## Toolbox configuration

JetBrains documents Toolbox user settings under:

`%LOCALAPPDATA%\JetBrains\Toolbox\.settings.json`

At least networking timeouts and OpenTelemetry settings use this documented file. Toolbox also exposes user settings such as tool installation location.

Sources:
- https://www.jetbrains.com/help/toolbox-app/frequently-asked-questions.html
- https://www.jetbrains.com/help/toolbox-app/otel.html

This is a plausible assimilation-directive surface, but do not blindly assimilate the whole Toolbox data directory. Account/license state, download/update caches, application metadata, and managed IDE state are separate.

## Toolbox-managed IDE versions

Toolbox explicitly supports installing multiple versions of the same IDE side by side. Its FAQ documents `Other versions` for installing another version alongside an existing one.

Source: https://www.jetbrains.com/help/toolbox-app/frequently-asked-questions.html

Toolbox 2.x also moved to stable/permanent tool paths while retaining side-by-side multiple versions.

Source: https://blog.jetbrains.com/toolbox-app/2023/08/toolbox-app-2-0-overhauls-installations-and-updates/

This makes Toolbox conceptually similar to a version manager for IDE products.

## Toolbox CLI maturity

JetBrains documents a Toolbox App CLI that can:

- install an exact IDE build using product code + build;
- detect externally installed JetBrains tools through Windows uninstall registry hives and common program directories.

However, JetBrains explicitly labels the CLI **very much work-in-progress**. It is currently distributed as a JAR and requires a JRE; the public documentation does not currently expose a complete stable list/uninstall lifecycle suitable for Machine-Soul ownership.

Source: https://www.jetbrains.com/help/toolbox-app/toolbox-app-cli.html

Recommendation: preserve Toolbox as the likely long-term IDE-version-management backend, but do not implement a hard dependency on the experimental CLI until its lifecycle surface is sufficiently stable/testable. Direct per-IDE installation remains a fallback option.

## IDE configuration directories

Rider and IntelliJ IDEA follow the shared IntelliJ-platform directory model.

Windows configuration:

`%APPDATA%\JetBrains\<product><version>`

Windows system/cache:

`%LOCALAPPDATA%\JetBrains\<product><version>`

User plugins normally live under the product/version configuration area.

Sources:
- https://www.jetbrains.com/help/rider/Directories_Used_by_the_IDE_to_Store_Settings_Caches_Plugins_and_Logs.html
- https://www.jetbrains.com/help/idea/directories-used-by-the-ide-to-store-settings-caches-plugins-and-logs.html

The config directory includes keymaps, schemes, file templates/types, inspections, options, templates, tools, and other user settings. System directories contain caches/local history and must not be assimilated wholesale.

Product/version-qualified directories mean a raw symlink of one whole config directory is a poor generic cross-version strategy.

## Settings export/import and Backup and Sync

Both current Rider and IntelliJ IDEA document:

- JetBrains Backup and Sync using JetBrains Account;
- manual `Export Settings` to a ZIP archive;
- manual `Import Settings` from a ZIP archive.

Synced/exported categories include themes, keymaps, color schemes, UI/system settings, editor settings, code styles, templates, and enabled/disabled plugin state.

Sources:
- https://www.jetbrains.com/help/rider/Sharing_Your_IDE_Settings.html
- https://www.jetbrains.com/help/idea/sharing-your-ide-settings.html

Rider adds another complication: some settings are layer-based (.NET/Rider settings), and export includes both directory-based settings and the global `This computer` layer.

Recommendation: prefer native export/import or supported settings surfaces over symlinking entire product-version config directories. Backup and Sync creates the same ownership question as VS Code Settings Sync: Machine-Soul must not silently fight the cloud-backed owner for the same categories.

## Plugins

Rider and IntelliJ IDEA both support command-line plugin installation by plugin ID:

`<ide executable> installPlugins <plugin-id ...>`

Toolbox-generated shell scripts may be used to address Toolbox-installed IDEs.

Sources:
- https://www.jetbrains.com/help/rider/Install_plugins_from_the_command_line.html
- https://www.jetbrains.com/help/idea/install-plugins-from-the-command-line.html

Plugins are executable/package state and should be modeled separately from raw IDE config. The VS Code comparison strongly supports a future reusable plugin/extension inventory concept, but synthesis should define the common model.

## Toolbox versus direct IDE ownership

Potential Machine-Soul modes:

1. Machine-Soul installs Toolbox; Toolbox owns IDE product/version lifecycle.
2. Machine-Soul installs individual IDEs directly through package-manager/native installers.
3. Hybrid discovery: Toolbox-managed and externally installed IDEs are both discoverable, but only one mechanism is preferred for new installations.

Toolbox itself recommends re-installing external tools through Toolbox when committing to Toolbox management, but can detect many externally installed tools.

Initial recommendation: prefer Toolbox as the conceptual IDE version manager **only after** its automation lifecycle is stable enough for exact install/check/uninstall ownership. Until then, do not make Toolbox ownership a prerequisite for managing IDE configuration or plugins.

## Rider versus IntelliJ comparison

Shared IntelliJ-platform behavior is substantial:

- product/version config directories;
- Backup and Sync;
- settings ZIP export/import;
- plugin Marketplace + CLI install;
- cache/system directories separate from config.

Rider-specific differences (notably layer-based settings) prove that product-specific overlays remain necessary. One generic `JetBrainsIDE` config blob would be dishonest.

## State to exclude

Do not assimilate:

- JetBrains Account tokens/license credentials;
- caches/indexes/local history;
- logs/crash dumps;
- Toolbox download/update caches;
- project-local `.idea` state that belongs in project repositories or is machine-specific;
- generated SDK/toolchain paths without an explicit portable model;
- entire plugin directories;
- machine-specific window/session/recent-project state unless deliberately selected.

## Capability recommendation

- **Toolbox install**: strong near-term USER-scoped WinGet candidate.
- **Toolbox `.settings.json`**: plausible config candidate once desired settings are selected.
- **IDE installation/version sets**: investigate implementation after Toolbox CLI maturity/behavior is experimentally validated; direct IDE package fallback remains possible.
- **IDE settings**: native export/import/Backup-and-Sync-aware strategy preferred over whole-directory symlink.
- **IDE plugins**: separate package/plugin inventory capability; compare with VS Code in final DEV synthesis.
- **IDE SDK/toolchain references**: likely depend on runtime/toolchain annexation findings later in this workstream.

## Promotion readiness

Toolbox installation can be promoted independently now.

Toolbox config, IDE settings/plugins, desired IDE product/version sets, and sync ownership require maintainer desired state and/or a stable automation choice before implementation.
