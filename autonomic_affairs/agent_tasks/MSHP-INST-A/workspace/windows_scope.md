# Windows installation scope investigation

Status: completed research output for `MSHP-INST-A-020`.

Research date: 2026-09-28.

## WinGet scope contract

Current Microsoft documentation exposes scope consistently across the WinGet surfaces needed by Machine-Soul:

- `winget install --scope user|machine` selects the installer target scope;
- `winget show --scope user|machine` selects installer information for that scope;
- `winget list --scope user|machine` filters installed-package results by installed scope;
- `winget uninstall --scope user|machine` filters the installed package selected for removal;
- `winget upgrade --scope user|machine` filters/selects installed scope for upgrade.

Sources:
- https://learn.microsoft.com/en-us/windows/package-manager/winget/install
- https://learn.microsoft.com/en-us/windows/package-manager/winget/show
- https://learn.microsoft.com/en-us/windows/package-manager/winget/list
- https://learn.microsoft.com/en-us/windows/package-manager/winget/uninstall
- https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade

### Preferences versus requirements

WinGet settings make the semantic distinction Machine-Soul needs:

- `installBehavior.preferences.scope` changes installer ordering. Microsoft documents the default preference as current-user scope with machine fallback when user scope is unavailable.
- `installBehavior.requirements.scope` filters installers. A requirement can leave no applicable installer and make installation fail.
- the command-line `--scope` parameter is the matching command-level scope control and overrides the corresponding settings requirement for that command.

Therefore ambient WinGet settings are unsuitable as Machine-Soul mutation policy. Machine-Soul should pass its own required scope for managed installs/removals.

Source: https://learn.microsoft.com/en-us/windows/package-manager/winget/settings

### Manifest scope

WinGet installer manifests may declare `Scope: user` or `Scope: machine` at the installer/root level. A package version may expose different installer nodes for different scopes. The schema also distinguishes `ElevationRequirement`; elevation behavior is not the same thing as installation scope.

Sources:
- https://github.com/microsoft/winget-pkgs/blob/master/doc/manifest/schema/1.12.0/installer.md
- https://github.com/microsoft/winget-pkgs/blob/master/doc/manifest/schema/1.28.0/installer.md

Requested required scope should therefore act as installer selection/filtering, not as a wish that may silently fall back. If no applicable installer exists, failure is the correct Machine-Soul result.

### Portable packages

WinGet has separate user- and machine-scope portable package roots (`portablePackageUserRoot` and `portablePackageMachineRoot`). This reinforces that portable installation still has meaningful user/machine scope even when its filesystem layout differs from MSI/MSIX.

Machine-Soul should not infer scope from path alone when WinGet can report/filter installed scope directly.

## Current Machine-Soul WinGet gaps

Current `WingetPackage` mutation passes no `--scope` for install or uninstall.

Current `WingetPackageDiscovery` executes one unscoped `winget list --id ... --exact` query and creates a scope-unknown correlation candidate.

Consequences:

1. managing WinGet's own scope preference could change which installer current MSHP selects;
2. user + machine instances cannot be represented as separate WinGet correlation candidates;
3. uninstall does not scope-filter the package it owns;
4. `InstallState` cannot record requested/actual scope;
5. `_state_matches()` currently matches manager + package identity without scope.

Minimum Windows fix therefore needs explicit scoped mutation **and** scoped discovery/provenance. Adding only `--scope` to install would be incomplete.

## Oh My Posh regression case

Machine-Soul currently manages `JanDeDobbeleer.OhMyPosh` through WinGet.

The current community manifest inspected during this task is version `31.3.0` (released 2026-09-13). It uses AppX/MSIX installers with package family `ohmyposh.cli_96v55e8n804z4`, and the installer manifest does **not** contain an explicit WinGet `Scope:` field.

Authoritative manifest:
https://github.com/microsoft/winget-pkgs/blob/master/manifests/j/JanDeDobbeleer/OhMyPosh/31.3.0/JanDeDobbeleer.OhMyPosh.installer.yaml

Native AppX installation/registration is user-account oriented, but the absence of WinGet manifest `Scope:` means implementation must validate current WinGet behavior when an explicit `--scope user` is supplied rather than assuming manifest metadata always declares the scope.

OMP should become a concrete integration/regression test for scoped WinGet behavior before Machine-Soul flips the strategy to an explicit user request.

## MSI / ARP

Windows Installer has true per-user and per-machine installation contexts. `ALLUSERS`, `MSIINSTALLPERUSER`, package authoring, and privileges determine which context is used.

Sources:
- https://learn.microsoft.com/en-us/windows/win32/msi/installation-context
- https://learn.microsoft.com/en-us/windows/win32/msi/allusers
- https://learn.microsoft.com/en-us/windows/win32/msi/msiinstallperuser

Windows Installer inventory APIs can enumerate per-machine and per-user installations, including other users when sufficient privileges/context are supplied.

Source: https://learn.microsoft.com/en-us/windows/win32/msi/inventory-products-and-patches-

Current Machine-Soul ARP discovery already maps HKCU records to `USER` and HKLM records to `MACHINE`. That is useful for the current execution user's registrations, but it is not a complete cross-user MSI inventory.

Because initial cross-account user mutation should be unsupported, current-user + machine discovery is enough for the first implementation. Full all-user MSI inventory remains a structured future gap.

## MSIX / AppX

`Add-AppxPackage` adds a signed package to a **user account**. `Get-AppxPackage` enumerates packages installed in user profiles; `-User`/`-AllUsers` can inspect other users with administrator permissions.

Sources:
- https://learn.microsoft.com/en-us/powershell/module/appx/add-appxpackage
- https://learn.microsoft.com/en-us/powershell/module/appx/get-appxpackage

Provisioning is a different concept: `Get-AppxProvisionedPackage` reports packages in the Windows image that will be installed for each new user. Provisioned image state should not be collapsed into the same `MACHINE` installation semantics as MSI/WinGet machine scope.

Source: https://learn.microsoft.com/en-us/powershell/module/dism/get-appxprovisionedpackage

Current Machine-Soul AppX discovery correctly uses `PACKAGE_USER` for current-user registration. A requested `USER` mutation may be considered compatible with a verified `PACKAGE_USER` result when the package subject is the same target/execution user.

## Execution account and cross-account user scope

WinGet's documented user scope is for the **current user**. The WinGet commands provide no ordinary `--user <other-account>` target parameter analogous to `Get-AppxPackage -User` discovery.

Therefore the Windows-first rule remains:

> A Machine-Soul `USER`-scope mutation is supported only when the logical target account is the current execution account. Non-current user scope is unsupported until a separately proven execution/impersonation mechanism exists.

Machine scope is different: elevation may change the security context used for privileged work, while the installation remains host/machine scoped.

## Scoped discovery and uninstall recommendation

For a managed WinGet package, the first implementation should:

1. declare one required Machine-Soul scope (`USER` or `MACHINE`);
2. add `--scope <scope>` to install;
3. query `winget list --scope user` and `--scope machine` separately when discovering a WinGet-correlated package so dual-scope instances remain distinct;
4. enrich/correlate those candidates with native ARP/AppX evidence where available;
5. after install, require a discovered candidate compatible with the requested scope before writing ownership provenance;
6. persist requested/actual scope and scope subject;
7. on uninstall, match provenance to one exact candidate and pass `--scope <actual scope>` to WinGet;
8. refuse if candidate matching is ambiguous rather than allowing WinGet to pick another scoped instance.

Machine-Soul's abstract requested `USER` scope may accept native `USER` or `PACKAGE_USER` observed scope when the subject is the intended current user. Requested `MACHINE` accepts only machine scope.

## Scenario validation

| Scenario | Windows result |
|---|---|
| Package offers user + machine; MSHP requires user | Pass `--scope user`; no fallback to machine. Verify user/package-user candidate before provenance. |
| Package offers only machine; MSHP requires user | WinGet has no applicable requested-scope installer; fail, do not fall back. |
| User + machine instances already coexist | Scoped list/discovery retains both. Managed state must identify one exact scope; uninstall scope-filters that one. |
| WinGet preference changes from user to machine | No semantic effect on MSHP-managed mutation because MSHP supplies explicit required scope. |
| Target account differs from current executor; requested user scope | Refuse before mutation. |
| Current OMP AppX manifest lacks `Scope:` | Treat as an explicit validation edge; verify `--scope user` behavior and post-install PACKAGE_USER evidence before claiming managed scope. |

## Windows-first implementation boundary

Windows/core implementation does **not** need full all-user MSI inventory, MSIX provisioning management, or arbitrary impersonation before it can be correct.

The bounded first implementation needs:

- core scope policy/provenance types;
- WinGet explicit scope install/list/uninstall;
- current-user/machine discovery separation;
- current-account guard for user scope;
- actual-scope post-verification;
- OMP regression coverage;
- machine-scope provenance namespace.

Full other-user inventory/impersonation remains an initiative gap unless a supported application later requires it.
