# Installation architecture

## 1. Separation from configuration

Application lifecycle and configuration lifecycle are independent:

```text
Install / Uninstall
    = make application capability exist or remove it

Apply / Unapply / Check
    = connect the application's native config files to tracked doctrine
```

A user may apply configuration to an already-installed application without the Hivemind claiming installation ownership.

Likewise, uninstalling an application must not silently destroy preserved user configuration.

## 2. Bootstrap-runtime rule

An application's installer must not require that application to already exist.

Therefore:

- Windows bootstrap/install operations use Windows-native PowerShell as the baseline runtime.
- Ubuntu/Linux bootstrap/install operations use POSIX/Bash-compatible machinery as the baseline runtime.
- Fish scripts must not be required to install Fish.
- Zsh scripts must not be required to install Zsh.
- Oh My Posh must not be required to install Oh My Posh.

Application-local entry points may be thin wrappers, but the underlying bootstrap path must remain callable from the platform baseline.

## 3. Installation strategy selection

Do not force every application through one universal package manager.

For each application/platform pair, choose an explicit installation strategy in this preference order:

1. supported native/system package manager when the package is suitable and upstream-supported;
2. upstream-supported package/installer mechanism;
3. upstream-supported standalone installer;
4. manual/download strategy when necessary;
5. source build only when intentionally selected.

The chosen strategy is application-specific and documented.

Examples observed during the 2026-09 investigation:

- Windows Package Manager supports exact-ID install/uninstall and is a strong Windows default when a suitable package exists.
- PowerShell documents WinGet as a supported Windows installation path.
- Oh My Posh documents WinGet on Windows and its own installer on Linux.
- Fish publishes platform/distribution installation guidance and is normally obtained through system/distribution mechanisms on Linux.
- Contour documents platform-specific packages/installers rather than one universal mechanism.

These are examples, not hard-coded global rules.

## 4. Exact package identity

Package-manager operations must prefer exact package IDs/names over fuzzy search results.

The module should document enough identity to avoid accidentally installing a similarly named package.

Where a package source matters, specify it explicitly.

## 5. Installation state and ownership

Installation has its own ownership model.

Before Install:

- detect whether the application already exists;
- determine whether its presence can be attributed to a previous successful Machine-Soul install operation.

If the application already exists but was not installed by the Hivemind, report an already-present/unmanaged state and do not fabricate ownership.

If the Hivemind installs an application successfully, record installation provenance under `scratch/state/`, including the strategy/package identity and useful version/path information.

## 6. Safe Uninstall

Uninstall should remove an application automatically only when ownership/provenance is sufficiently understood.

If an application predated Machine-Soul management, Uninstall should not casually remove it.

A future explicit override may allow deliberate removal, but “we found the executable” is not proof that the Hivemind owns its installation.

Configuration Unapply and application Uninstall remain separate operations.

## 7. Idempotency

Install should be safe to repeat:

- already correctly installed and Hivemind-managed → report success/already installed;
- already installed but unmanaged → report that state without taking ownership silently;
- missing → install using the declared platform strategy.

Uninstall should similarly tolerate an already-absent managed target without destructive failure.

## 8. Privilege scope

Do not elevate an entire workflow merely because one package-manager step needs administrator/root privileges.

Prefer:

1. preflight unprivileged checks;
2. elevate only the native install/uninstall command that requires it;
3. return to normal privilege for repository/state/config work.

Root-specific configuration is a target account concern, not justification for running unrelated user operations as root.

## 9. Network/download behavior

Install operations may need the network. They should:

- identify the source/strategy being used;
- fail clearly when network/package metadata is unavailable;
- avoid silently switching to an unrelated fallback source;
- preserve enough metadata to understand what was installed.

Where an upstream installation method executes downloaded code, prefer a mechanism that remains inspectable/testable and document the trust boundary.

## 10. Uninstall does not imply config destruction

Removing an application does not automatically delete backups or canonical tracked configuration.

If native package uninstall leaves application configuration behind, that behavior should be understood and reported rather than “cleaned up” by guessing.

The user may separately Unapply configuration if desired.


## 11. Discovery is independent from installation strategy

Installation discovery is a separate capability from Install/Uninstall.

An application may expose rich `check_installed` discovery even when Machine-Soul has no safe installation strategy for it. Built-in components, externally installed tools, and applications with many supported upstream installation methods are all examples.

The preferred install strategy remains one input to discovery: it defines what Machine-Soul considers a preferred or compatible package identity. It is not the discovery implementation itself.

Discovery should gather candidate facts from declared reusable discovery strategies/hints, then assess:

- application presence;
- candidate identities, versions, paths, and scopes;
- native/package registration;
- preferred-strategy match and manageability;
- Machine-Soul ownership;
- ambiguity or unknown state.

Package/catalog correlation must not be presented as historical installer provenance unless the platform exposes evidence that actually proves it. WinGet can correlate/manage software installed by other means, and a dpkg package does not prove whether apt or direct dpkg installation originally acquired it.

See [`DISCOVERY_SEMANTICS.md`](DISCOVERY_SEMANTICS.md) and the DISC-A installation-discovery workspace for the detailed evidence map.


## 12. Concrete discovery-plan surface

`PlatformDeclaration.installation_discovery` owns read-only installation discovery independently from `install_strategy`.

A declaration may therefore support `check_installed` while Install/Uninstall remain unsupported or not implemented. Conversely, an install strategy does not implicitly authorize discovery semantics.

The shared discovery engine consumes ordered reusable descriptors such as exact dpkg package identity, exact WinGet package correlation, and executable identity. Platform-specific tasks may enrich those descriptors/backends, but generic operation code must not branch on application IDs.

The current `check_installed` operation serializes a typed `InstallationAssessment` beneath `OperationResult.data["assessment"]`. Presence may be `present`, `absent`, `ambiguous`, or `unknown`; backend unavailability must not become false absence.

Install/Uninstall continue to use `install_strategy` and Machine-Soul provenance for mutation safety. Discovery does not claim/adopt ownership.


## 13. Linux discovery implementation

Current Linux discovery combines exact dpkg registration where Machine-Soul has a verified package identity with executable/path/version observations.

For exact dpkg packages, discovery records package registration, version/architecture when available, and verifies whether the resolved executable is owned by that package. A package registration and its package-owned PATH executable are merged into one installation candidate.

A separately resolved executable that is not owned by the registered package remains a distinct candidate. This intentionally surfaces cases such as a distro Fish package plus a manually installed Fish earlier on PATH as ambiguous rather than silently choosing one.

Current declarations:

- Bash: exact Debian-family `bash` package plus executable fallback.
- Zsh: exact Debian-family `zsh` package plus executable fallback.
- Fish: exact `fish` package is preferred-strategy compatible, plus executable fallback for manual/source installs.
- Oh My Posh: executable/version discovery, matching upstream's user-local install-script model.
- Contour: executable/version discovery with opportunistic dpkg-owner enrichment. Upstream documents Ubuntu `.deb`, multiple distro packages, Flatpak, and source installs; no Flatpak ID is guessed without a verified identity.

Missing optional dpkg tooling does not erase an executable candidate. It remains a present installation with weaker/partial evidence and an explanatory backend error.

Current upstream references used for the Linux declaration choices:

- https://fishshell.com/
- https://ohmyposh.dev/docs/installation/linux
- https://contour-terminal.org/install/
