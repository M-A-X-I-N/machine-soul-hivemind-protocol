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
| Fish | Ubuntu/Linux | Supported via `apt` | Supported via `apt` | state under `scratch/state/install` |
| Oh My Posh | Windows | Supported via exact-ID WinGet | Supported via exact-ID WinGet | state under `scratch/state/install` |

Other application install/uninstall operations remain `NOT_IMPLEMENTED` until a safe platform strategy is added.

A pre-existing installation is reported as unmanaged and is never silently claimed for later uninstall.

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
