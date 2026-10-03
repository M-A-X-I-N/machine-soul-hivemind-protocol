# Linux installation scope extensibility investigation

Status: completed research output for `MSHP-INST-A-030`.

Research date: 2026-09-28.

## Purpose

This task stress-tests the core scope model against representative Linux package-management shapes. It does **not** taskify or implement those managers.

## Apt / dpkg — fixed machine scope

Current Machine-Soul Apt mutation uses `apt-get` through root/sudo when required. Debian dpkg documentation describes the system package database under `/var/lib/dpkg` and the default install root `/`; privileged mutation updates that system database/filesystem.

Therefore `AptPackage` is correctly modeled as a backend with **fixed MACHINE scope**.

`sudo`/root is only execution privilege. It is not evidence of a separate installation scope and does not make the invoking/target account the owner of the package.

Current account-nested `InstallState` storage is therefore semantically wrong for Apt ownership and should migrate to a host/machine namespace.

Sources:
- https://manpages.debian.org/trixie/dpkg/dpkg.1.en.html
- https://manpages.debian.org/testing/dpkg/dpkg.1.en.html

## Flatpak — explicit user/system plus named system installation identity

Flatpak makes scope first-class:

- `--user` targets the per-user installation;
- `--system` targets the default system-wide installation;
- `--installation=NAME` targets a named system-wide installation defined under `/etc/flatpak/installations.d/`;
- installation/list/info/uninstall/update surfaces expose these selectors consistently;
- commands that search both user/system can become ambiguous when the same ref exists in multiple installations.

Source:
- https://docs.flatpak.org/en/latest/flatpak-command-reference.html

Flatpak therefore fits the core USER/MACHINE scope classes **but** proves that `MACHINE` alone is insufficient for exact identity. A future Flatpak candidate/provenance record needs the backend-specific installation name (`default` or another NAME) as part of exact mutation/uninstall targeting.

Machine-Soul should use explicit scope/installation selectors rather than Flatpak command defaults. No Flatpak task is created now.

## pipx — selectable user/global with configurable roots

pipx defaults to per-user application state:

- `PIPX_HOME`: normally `~/.local/share/pipx` on Linux;
- `PIPX_BIN_DIR`: normally `~/.local/bin`;
- `PIPX_MAN_DIR`: normally `~/.local/share/man`.

Current pipx also supports `--global`, documented as an all-users/system-wide action, with defaults such as `/opt/pipx` and `/usr/local/bin`. The global and user roots can be overridden independently through environment variables. `pipx environment` exposes the resolved paths.

Sources:
- https://pipx.pypa.io/latest/reference/environment-variables.html
- https://pipx.pypa.io/latest/how-to/configure-paths.html
- https://pipx.pypa.io/stable/reference/cli.html
- https://pipx.pypa.io/stable/explanation/how-pipx-works.html

This fits a future required USER/MACHINE mutation policy, while resolved home/bin/man roots remain backend-specific evidence needed for exact ownership and verification.

The existence of `--global` must not be confused with how the pipx executable itself was installed (distribution package, user pip install, etc.). Package-manager installation of pipx and pipx-managed application scope are separate layers.

## Homebrew / Linuxbrew — prefix + owning account, not a simple package scope flag

Homebrew on Linux uses the default prefix `/home/linuxbrew/.linuxbrew` so routine formula management does not require sudo. Official Homebrew documentation states that Homebrew is designed for **one owning account**, which may be a dedicated account. Other users may be able to read/execute installed software, and current Homebrew provides mechanisms such as `brew as-brew-user` for performing management as the owning account.

Sources:
- https://docs.brew.sh/Installation
- https://docs.brew.sh/FAQ
- https://docs.brew.sh/Homebrew-on-Linux
- https://docs.brew.sh/Manpage

This is intentionally not forced into a new core scope enum.

A future Homebrew backend needs at least:

- Homebrew prefix;
- owning/managing account;
- formula/keg identity;
- any relevant shared-execution policy;
- exact Homebrew instance selected for mutation.

The coarse observed scope classification may ultimately be USER, MACHINE, or UNKNOWN depending on the supported Machine-Soul policy, but the investigation does not decide that prematurely. The important architectural fact is that backend-specific installation identity can be more important than a single global/user flag.

Homebrew therefore stress-tests the separation between:

- execution identity;
- owner/manager account;
- coarse installation scope;
- backend-specific mutation target.

No Homebrew task is created now.

## Common core versus backend-specific responsibilities

### Core responsibilities

- represent requested mutation scope policy independently from observed scope;
- retain coarse actual scope (`USER`, `MACHINE`, `PACKAGE_USER`, `UNKNOWN`);
- retain scope subject when an account matters;
- compare requested/fixed scope against actual discovered scope;
- choose provenance namespace based on actual scope;
- require exact candidate ownership before uninstall;
- refuse ambiguous/unreconciled scope;
- make intentional delegation/fallback explicit rather than inheriting command defaults.

### Backend responsibilities

- translate core policy into native selectors (`--scope`, `--user`, `--system`, `--global`, etc.);
- expose whether a requested scope is supported;
- report native installation identity beyond the coarse scope;
- expose backend-specific roots/prefixes/installation names;
- perform native discovery sufficient to verify actual scope;
- build an exact uninstall target;
- handle privilege/elevation without confusing it with scope.

## Representative compatibility table

| Backend pattern | Core scope | Extra identity | Scope selection |
|---|---|---|---|
| Apt/dpkg | fixed MACHINE | package/database identity | inherent/fixed |
| Flatpak user | USER | user installation + ref | explicit `--user` |
| Flatpak system | MACHINE | named system installation + ref | `--system` / `--installation=NAME` |
| pipx default | USER | resolved PIPX roots + venv/package metadata | default/user semantics; future MSHP should be explicit |
| pipx global | MACHINE | resolved global roots + metadata | explicit `--global` |
| Homebrew/Linuxbrew | backend-specific/coarse scope requires implementation decision | prefix + managing account + formula/keg | select correct Homebrew instance/owner |

## Scenario validation

| Scenario | Required model behavior |
|---|---|
| Apt run through sudo for a normal target account | Execution identity may elevate; install remains MACHINE; provenance belongs to host/machine. |
| Same Flatpak ref in user and system installation | Keep candidates separate; exact installation identity required for uninstall. |
| Named Flatpak system installation | Core MACHINE + backend installation name; do not invent another core scope enum. |
| pipx default roots overridden under current user | Still user-oriented if backend proves that policy; preserve resolved roots in metadata. |
| pipx `--global` with overridden global roots | MACHINE plus actual resolved root metadata. |
| Dedicated Linuxbrew owner with binaries executable by other accounts | Owner/executor/prefix are distinct facts; do not infer machine ownership merely because other users can execute binaries. |

## Deferred gaps

Flatpak, Homebrew/Linuxbrew, pipx, Snap, Nix, language-specific managers, AppImage-like models, and other future mechanisms remain initiative gaps unless Machine-Soul actually adds them.

No incomplete executable tasks should exist merely to represent those gaps.

## Implementation implication

Nothing discovered here blocks the Windows/core implementation.

The core model from `MSHP-INST-A-010` remains sufficient if backend-specific exact identity is first-class metadata and future strategy interfaces can:

- declare fixed or selectable scope behavior;
- translate scope policy natively;
- discover/verify actual scope;
- return an exact backend-specific mutation target.
