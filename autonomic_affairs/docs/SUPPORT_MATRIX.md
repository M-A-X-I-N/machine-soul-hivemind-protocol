# Support matrix

This document describes the current `main` Python/declarative implementation state. It is intentionally explicit about capability gaps.

## Configuration operations

Legend:

- **Supported** — Apply / Unapply / Check are implemented.
- **Not implemented** — the configuration exists, but a safe native adapter is not yet selected.
- **Not applicable** — the application is not part of the current host target.

| Application | Windows host variant | Ubuntu/Linux host variant | Ubuntu-like host variant |
|---|---|---|---|
| Windows Terminal | Supported | Not applicable | Not applicable |
| PowerShell | Supported | Not applicable | Not applicable |
| CMD | Supported | Not applicable | Not applicable |
| Fish | Supported via Python wrapper in POSIX compatibility environment | Supported | Supported |
| Bash | Supported via Python wrapper in POSIX compatibility environment | Supported | Supported |
| Zsh | Supported via Python wrapper in POSIX compatibility environment | Supported | Supported |
| Oh My Posh | Supported | Supported | Supported |
| Contour | Supported | Supported | Supported |

### Windows Fish/Bash/Zsh compatibility environment

The canonical entry points are the same platform-neutral Python wrappers used everywhere else.

Their Windows declarations select `WindowsPosixHomeDestination`. That shared strategy reads the compatibility environment's real `HOME` and uses `cygpath` only for the platform-specific path translation required to reach the native Windows destination.

There is no parallel Bash or PowerShell configuration engine. When the required compatibility environment is absent, destination resolution reports the operation unavailable instead of guessing a path.

## Account-specific OMP

The following tracked OMP targets exist and are covered by CI matrix tests:

- each current Linux host variant / normal target account;
- each current Linux host variant / privileged target account;
- the current Windows host variant / common configuration.

Linux shell configs select the user-specific OMP file first and fall back to host common only when one exists.

## Installation lifecycle

Current managed installation examples:

| Application | Platform | Install | Uninstall | Ownership model |
|---|---|---|---|---|
| Fish | Ubuntu/Linux | Supported via fixed-machine `apt` | Supported via fixed-machine `apt` | host/machine-scoped exact provenance |
| Oh My Posh | Windows | Supported via exact-ID WinGet with explicit user scope | Supported via exact-ID WinGet with explicit owned scope | scoped user/package-user exact provenance |
| Visual Studio Code | Windows | Supported via exact `Microsoft.VisualStudioCode` WinGet identity | Supported for exact owned USER-scoped install | scoped user/package-user exact provenance |
| JetBrains Toolbox | Windows | Supported via exact `JetBrains.Toolbox` WinGet identity | Supported for exact owned USER-scoped install | scoped user/package-user exact provenance |
| Python Install Manager | Windows | Supported via exact Microsoft Store/WinGet identity | Supported for exact owned USER-scoped install | scoped user/package-user exact provenance |

Visual Studio Code and JetBrains Toolbox are intentionally **install-only**: Machine-Soul does not yet own editor/IDE settings, profiles, extensions/plugins, Sync, or selected IDE versions. nvm-windows is discoverable as a manager/tool but its own installation lifecycle remains unclaimed; Node runtime lifecycle is handled separately by the runtime backend.

Other application install/uninstall operations remain `NOT_IMPLEMENTED` until a safe platform strategy is added.

A pre-existing installation is reported as unmanaged and is never silently claimed for later uninstall.

Managed installation scope is explicit. WinGet mutation does not inherit ambient `settings.json` scope preferences, and Apt is modeled as fixed machine scope. User- and machine-scoped instances may coexist; uninstall requires exact scoped ownership/candidate matching. Legacy scope-less provenance is treated as unreconciled until a backend can prove one safe migration.

## Developer runtime and package lifecycle

The first developer-annexation runtime/package phase is implemented as library/backend capabilities with explicit desired state rather than inferred global inventories.

| Layer | Windows capability | Important boundary |
|---|---|---|
| Python runtimes | Official Python Install Manager exact per-user multiversion set + explicit default | unmanaged/legacy Python remains visible but unowned |
| Node runtimes | nvm-windows v2 exact per-user multiversion set + explicit default | manager migration, Corepack, and project pins remain separate |
| Lua/LuaJIT runtimes | exact Machine-Soul-owned versioned prefixes + explicit launcher selection | native source builds require explicit trusted source/digest and native-toolchain prerequisites |
| pip environments | exact interpreter-bound package environments | project/external environments are not silently adopted |
| npm global packages | exact Node runtime + resolved global-prefix environments | `npm -g` is never treated as machine-global state |
| LuaRocks trees | exact owned Lua/LuaJIT runtime + exact rocks-tree environments | distinct runtimes use distinct trees; project trees remain project-owned |

Runtime default/selection state is independent from package desired roots. An owned package environment blocks removal of its exact runtime until the package-environment ownership is resolved. Matching versions under another manager/backend do not migrate automatically.

No maintainer-selected runtime/package inventory is invented by these capabilities. Project-local dependency manifests, lockfiles, virtual environments, local `node_modules`, and LuaRocks project trees remain project-owned unless a future explicit policy says otherwise.

## Validation coverage

CI currently exercises:

- shared Python Linux and Windows configuration lifecycle;
- preservation/restoration of existing config files;
- wrong and broken symlink classification;
- prompt-decline safety;
- external mutation protection;
- Linux and Windows application wrappers;
- CMD AutoRun preservation/restoration;
- install dry-run/provenance behavior;
- `$MACHINE_SOUL` checkout relocation while preserving the original restore lineage;
- root/normal-account separation including an actual Ubuntu `sudo` process;
- Linux host variants × normal/privileged target-account config resolution;
- fresh remote clones on Windows and Ubuntu;
- developer-annexation integration across install-only editors, simultaneous Python/Node/Lua runtime sets, independent default selection, runtime-bound package ownership, unknown-package preservation, blocked runtime removal, project-owned refusal, backend-migration refusal, and credential non-persistence.


## Installation discovery

Installation discovery is broader than managed installation.

| Application | Windows discovery | Linux discovery |
|---|---|---|
| Bash | Supported in active MSYS2/Cygwin-style environment | Supported via dpkg + executable evidence |
| Zsh | Supported in active MSYS2/Cygwin-style environment | Supported via dpkg + executable evidence |
| Fish | Supported in active MSYS2/Cygwin-style environment | Supported via preferred dpkg package + executable evidence |
| Oh My Posh | Supported via exact WinGet correlation + executable evidence | Supported via executable/version evidence |
| PowerShell | Supported via WinGet/MSIX/ARP/executable/built-in Windows PowerShell evidence | Not applicable |
| Windows Terminal | Supported via exact WinGet/MSIX/executable evidence | Not applicable |
| Contour | Supported via ARP/executable evidence | Supported via executable evidence with opportunistic dpkg ownership |
| CMD | Supported as a built-in Windows capability | Not applicable |
| Visual Studio Code | Supported via exact WinGet/executable evidence | Not applicable |
| JetBrains Toolbox | Supported via exact WinGet/executable evidence | Not applicable |
| Python Install Manager | Supported via exact Microsoft Store/WinGet/executable evidence | Not applicable |
| nvm-windows | Supported via executable/manager discovery | Not applicable |

Discovery can report present, absent, ambiguous, or unknown. Preferred-strategy compatibility and Machine-Soul ownership remain separate dimensions; neither implies historical installer provenance.

## Effective configuration verification

| Application | Windows verification | Linux verification | Evidence ceiling |
|---|---|---|---|
| Bash | Supported in active POSIX compatibility environment | Supported | Runtime startup trace |
| Zsh | Supported in active POSIX compatibility environment | Supported | Runtime startup trace |
| Fish | Supported in active POSIX compatibility environment | Supported | Resolution |
| Oh My Posh | Supported | Supported | Application theme probe + runtime consumer-shell selection when available |
| PowerShell | Supported | Not applicable | Resolution, strengthened indirectly through OMP consumer verification when applicable |
| Windows Terminal | Supported | Not applicable | Resolution |
| Contour | Supported | Supported | Application-native config probe when available, otherwise weaker evidence |
| CMD | Supported | Not applicable | Resolution |

Verification evidence strength is reported separately from the semantic conclusion. A supported verifier may legitimately return indeterminate; that is not the same as NOT_IMPLEMENTED.

## Integrated status

The broad manager exposes a read-only three-dimensional status workflow:

```text
python annexation_procedures/manage_machine_soul.py --workflow status
python annexation_procedures/manage_machine_soul.py --workflow status --json
```

For every discovered application it preserves independent installation, structural configuration, and effective-configuration results. There is deliberately no overall health score.
