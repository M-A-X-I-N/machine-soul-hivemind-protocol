# Support matrix

This document describes the current `experimental/v2` implementation state. It is intentionally explicit about capability gaps.

## Configuration operations

Legend:

- **Supported** — Apply / Unapply / Check are implemented.
- **Not implemented** — the configuration exists, but a safe native adapter is not yet selected.
- **Not applicable** — the application is not part of the current host target.

| Application | spaceship / Windows | workhorse / Ubuntu | runar / Ubuntu-like |
|---|---|---|---|
| Windows Terminal | Supported | Not applicable | Not applicable |
| PowerShell | Supported | Not applicable | Not applicable |
| CMD | Supported | Not applicable | Not applicable |
| Fish | Not implemented | Supported | Supported |
| Bash | Not implemented | Supported | Supported |
| Zsh | Not implemented | Supported | Supported |
| Oh My Posh | Supported | Supported | Supported |
| Contour | Supported | Supported | Supported |

### Windows Fish/Bash/Zsh gap

Tracked `spaceship` configs exist, but Apply/Unapply/Check intentionally return `NOT_IMPLEMENTED` from the PowerShell-side adapter.

Reason: on Windows these shells normally live inside a compatibility/runtime environment such as MSYS2 or Cygwin, and their effective `$HOME`, path translation, and symlink semantics are environment-specific. Selecting one silently would risk managing the wrong config file or creating something that is not a native file symlink.

The eventual adapter should explicitly model the chosen runtime(s) rather than guessing.

## Account-specific OMP

The following tracked OMP targets exist and are covered by CI matrix tests:

- `workhorse / m-a-x-i-n`
- `workhorse / root`
- `runar / m-a-x-i-n`
- `runar / root`
- `spaceship / common`

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

- shared Linux and Windows symlink lifecycle;
- preservation/restoration of existing config files;
- wrong and broken symlink classification;
- prompt-decline safety;
- external mutation protection;
- Linux and Windows application wrappers;
- CMD AutoRun preservation/restoration;
- install dry-run/provenance behavior;
- `$MACHINE_SOUL` checkout relocation while preserving the original restore lineage;
- root/normal-account separation including an actual Ubuntu `sudo` process;
- workhorse/runar × m-a-x-i-n/root config resolution;
- fresh remote clones on Windows and Ubuntu.
