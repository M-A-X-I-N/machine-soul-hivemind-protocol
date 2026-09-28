# Windows configuration candidate investigation

Status: completed research output for `MSHP-APPS-A-010`.

Research date: 2026-09-28.

## Inclusion criteria

A strong Machine-Soul application-config candidate should have most of these properties:

- stable/documented configuration contract rather than reverse-engineered mutable state;
- meaningful maintainer preferences worth carrying across machines;
- clear user/machine scope and destination/adapter semantics;
- safe separation from credentials, caches, session state, and machine-generated IDs;
- deterministic Apply/Unapply/Check semantics;
- an honest effective-verification story or an explicit decision that Verify is not yet available;
- enough portability that Git-managed desired state is useful.

Being technically copyable from AppData or the registry is not sufficient.

## Candidate matrix

| Candidate | Classification | Configuration contract | Likely Machine-Soul shape |
|---|---|---|---|
| Windows Terminal | Already managed | Documented `settings.json` | Existing file-level managed config baseline |
| WinGet client settings | **Strong implementation candidate** | Documented per-user JSON + schema; `winget settings` / `settings export` | Managed user JSON with WinGet-aware destination resolution; keep admin settings/sources separate |
| WSL global `.wslconfig` | **Strong implementation candidate** | Documented `%UserProfile%\.wslconfig` | Simple per-user singleton file; WSL restart semantics |
| OpenSSH client config | **Strong implementation candidate** | Documented `%UserProfile%\.ssh\config` | Simple per-user singleton file; strictly exclude keys/known_hosts |
| PowerToys | **Conditional / special-model candidate** | Official Microsoft DSC get/set/test/export resources + built-in backup/restore | Native declarative adapter, not symlink to internal AppData files |
| Windows Sandbox | **Conditional / asset-model candidate** | Documented `.wsb` XML launch profiles and newer `wsb` CLI | Track reusable launch-profile assets; not a singleton application config |
| File Explorer / Advanced Windows Settings | **Not an application-config candidate** | Documented Windows settings/policy/registry surfaces | Future OS-state/registry-policy domain, not an Explorer app entry |
| Notepad | **Not suitable at present** | UI settings exist, but no documented ordinary settings file/export contract found; package state includes opaque/binary session data | Do not manage internal LocalState/session blobs |

## 1. WinGet / Windows Package Manager client settings

### Contract and scope

Current Microsoft documentation explicitly describes WinGet client settings as user-customizable JSON. `winget settings` opens the settings file, the document publishes a JSON schema, and current WinGet 1.28 documentation exposes `winget settings export`.

Authoritative sources:

- https://learn.microsoft.com/en-us/windows/package-manager/winget/settings
- https://github.com/microsoft/winget-cli/blob/master/doc/Settings.md

The packaged WinGet settings path documented by the WinGet repository is:

`%LOCALAPPDATA%\Packages\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\LocalState\settings.json`

A source-built/unpackaged WinGet uses:

`%LOCALAPPDATA%\Microsoft\WinGet\Settings\settings.json`

The settings are per-user. They contain genuine desired-state preferences such as visual/logging behavior, source update timing, installer preferences/requirements, install roots, download behavior, telemetry, and network behavior.

### Important separation

Do not collapse these distinct WinGet surfaces:

1. **User client `settings.json`** — the strong file-config candidate.
2. **Administrator settings** — manipulated through `winget settings set/reset`; policy-like native state, not the user JSON file.
3. **Sources** — managed through `winget source add/edit/list/remove/reset/export`; separate native state and may require elevation.
4. **WinGet Configuration / DSC** — a configuration orchestration feature, not the WinGet client's own settings file.
5. **Package export/import** — installed-package inventory, unrelated to client preferences.

Microsoft currently documents `winget source export`, and source changes are an independent security/trust surface. They should not be silently reconstructed from `settings.json`.

Source: https://learn.microsoft.com/en-us/windows/package-manager/winget/source

### Deployment recommendation

File-level management is appropriate for **user settings.json**, but the destination resolver should distinguish packaged versus unpackaged WinGet rather than hard-code one environment blindly.

Because current MSHP WinGet install/uninstall now passes explicit scope, a tracked `installBehavior.preferences.scope` or `requirements.scope` cannot silently redefine Machine-Soul-controlled package scope. This was the reason installation-scope work took precedence.

Structural Check is straightforward. Effective Verify could eventually use WinGet's native settings/export surface as application evidence, but exact semantic comparison should be designed against the actual `settings export` format rather than assumed.

### Secrets/generated state

No credentials should be put in the tracked file. Logs, caches, package state, portable links/packages, and source databases are outside this config boundary.

## 2. WSL global `.wslconfig`

Microsoft documents `%UserProfile%\.wslconfig` as the global Windows-side configuration file for all WSL 2 distributions. It is distinct from `/etc/wsl.conf`, which lives inside each distribution.

Source: https://learn.microsoft.com/en-us/windows/wsl/wsl-config

The file does not exist by default and is intended to be user-created/edited. This is an excellent canonical singleton file candidate.

### Deployment recommendation

- scope: per Windows user;
- destination: `HomeRelativeDestination('.wslconfig')` or equivalent Windows user-profile strategy;
- format: INI-like documented WSL configuration;
- Apply/Unapply/Check: ordinary safe file-level Machine-Soul lifecycle;
- effective reload: WSL must stop and restart; Microsoft documents `wsl --shutdown` as the fast path;
- effective Verify: not all settings expose a uniform runtime query, so do not pretend structural application proves every setting is effective. A future verifier may support selected properties only.

Machine-specific resource values (for example memory/processors) may be intentionally host-specific rather than common configuration.

## 3. Windows OpenSSH client config

Microsoft documents the Windows OpenSSH client lookup order including the per-user file:

`%UserProfile%\.ssh\config`

and a system-wide `%ProgramData%\ssh\ssh_config`.

Source: https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration

### Deployment recommendation

The **per-user client config** is a strong file-level candidate:

- scope: per user;
- format: normal OpenSSH `ssh_config` syntax;
- destination: `%UserProfile%\.ssh\config`;
- structural Apply/Unapply/Check: ordinary managed file lifecycle.

### Security boundary

Only `config` belongs in the tracked config entry. Explicitly exclude:

- private keys;
- public/private credential material;
- `known_hosts` / host-key observations;
- sockets/control paths;
- agent state;
- generated host keys;
- server `sshd_config` unless separately designed as machine/service configuration.

Effective Verify can use `ssh -G <host>` to inspect resolved client options **only when the tracked config defines a stable probe host/alias with expected values**. Without such desired content, generic verification should remain unimplemented rather than invent a host.

## 4. PowerToys

PowerToys is a strong conceptual candidate but a poor symlink candidate.

Microsoft now documents modern DSC support with individual resource types such as `Microsoft.PowerToys/AppSettings`, `FancyZonesSettings`, `PowerLauncherSettings`, and many others. The bundled `PowerToys.DSC.exe` supports module enumeration and get/set/test/export-style operations; Microsoft documentation even demonstrates exporting every module for backup and restoring them.

Sources:

- https://learn.microsoft.com/en-us/windows/powertoys/dsc-configure/overview
- https://learn.microsoft.com/en-us/windows/powertoys/dsc-configure/microsoft-dsc
- https://github.com/microsoft/PowerToys/blob/main/doc/dsc/settings-resource.md

PowerToys also has a built-in Backup & Restore UI, but DSC is a better Machine-Soul fit because it expresses desired state and provides native get/test/set semantics.

Internal settings JSON files exist under PowerToys AppData, but the supported native DSC surface should be preferred over coupling MSHP to module implementation files.

### Recommendation

Do not add PowerToys as an ordinary file-symlink application. When canonical PowerToys desired settings are chosen, first add a reusable/native declarative configuration strategy that can:

- carry tracked module desired state;
- call native DSC get/test/set/export;
- produce ordinary Machine-Soul `OperationResult` semantics;
- distinguish portable common preferences from machine-specific layouts/paths/workspaces;
- support Unapply/restoration only with a deliberate backup/provenance design.

Because the maintainer has not yet supplied desired PowerToys module state, this remains structured deferred work rather than an executable implementation task.

## 5. Windows Sandbox

Microsoft documents `.wsb` XML configuration files for custom sandbox launches. They can configure vGPU, networking, mapped folders, logon command, audio/video input, protected client, printers, clipboard, and memory. Newer Windows versions also expose a `wsb` CLI that can start a sandbox with inline/custom config.

Sources:

- https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-configure-using-wsb-file
- https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli

These files are **launch profiles**, not one canonical application settings file. A user may intentionally have many.

### Recommendation

Track useful `.wsb` files as reusable assets/profiles if desired, but do not force them into the current one-application/one-config Apply model. Mapped folder paths and logon commands may be machine-specific and security-sensitive. A future profile/asset abstraction would fit better.

Device-wide Sandbox policy is another distinct surface (`WindowsSandbox` policy CSP / Group Policy) and should not be conflated with `.wsb` profiles.

## 6. File Explorer / Windows Advanced Settings

Microsoft now documents an Advanced Settings page exposing developer/power-user File Explorer preferences such as showing file extensions, hidden/system files, and full path in the title bar. Microsoft also publishes Windows settings/registry and ADMX/Policy CSP mappings for many Explorer options.

Sources:

- https://learn.microsoft.com/en-us/windows/advanced-settings/
- https://learn.microsoft.com/en-us/windows/apps/develop/settings/settings-windows-11
- https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-windowsexplorer

This is real desired state, but it is **Windows OS/shell state**, not a conventional application config file. It points toward a future reusable registry/policy/Windows-settings strategy rather than an `explorer` application entry.

Do not taskify it from this app-config investigation without a separate OS-state design decision.

## 7. Notepad

Current Notepad has user-visible settings, and Microsoft documents policy controls for some features (for example disabling AI features). However, this investigation found no Microsoft-supported ordinary user-settings file/export/import contract comparable to Terminal/WinGet/WSL/OpenSSH.

Microsoft documentation:

- https://learn.microsoft.com/en-us/windows/client-management/manage-notepad

Community reverse engineering shows modern Notepad package LocalState includes binary tab/window/session state. That is precisely the kind of opaque/generated state Machine-Soul should **not** track as configuration.

Therefore Notepad is not suitable for Machine-Soul ordinary config management at present. If Microsoft later exposes a supported settings/export/DSC interface, reconsider it.

## Implementation readiness / promotion

Three candidates are technically ready for ordinary application integration **once canonical desired content is chosen**:

1. WinGet user settings JSON;
2. WSL global `.wslconfig`;
3. OpenSSH client `config`.

The maintainer has not yet selected/imported those desired settings. Creating executable integration tasks now would force the agent either to invent preferences or to deploy empty/default files that could overwrite real unmanaged configuration. That would violate Machine-Soul's safety model.

PowerToys is also promising, but needs desired module state plus a native DSC configuration strategy.

Accordingly, this investigation records these as structured initiative work rather than immediately executable tasks. Promotion into tasks should happen when the canonical desired state is supplied or explicitly authorized to be captured/imported.

Windows Sandbox profiles and Windows OS/shell settings remain separate model questions, not blocked ordinary application tasks.
