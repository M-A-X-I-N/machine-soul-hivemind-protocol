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

Other application install/uninstall operations remain `NOT_IMPLEMENTED` until a safe platform strategy is added.

A pre-existing installation is reported as unmanaged and is never silently claimed for later uninstall.

Managed installation scope is explicit. WinGet mutation does not inherit ambient `settings.json` scope preferences, and Apt is modeled as fixed machine scope. User- and machine-scoped instances may coexist; uninstall requires exact scoped ownership/candidate matching. Legacy scope-less provenance is treated as unreconciled until a backend can prove one safe migration.

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
- fresh remote clones on Windows and Ubuntu.


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
