# MSHP-PLATFORM-COVERAGE — Windows 11, Debian/Ubuntu Server and Arch-family support

**Status:** OPEN

## Goal

Prioritize reproducible desired machine state on Windows 11 and Debian-based/Ubuntu Server hosts, eventually extending managed installation to Manjaro/Arch-family machines.

## Current state / coverage

Current MSHP documentation and tests cover Windows and Ubuntu/Linux host variants, scoped WinGet/Apt installation and multi-version developer runtimes. No comprehensive fresh-machine inventory has been selected.

## Known gaps

- Identify uncovered Windows 11 and Debian/Ubuntu Server life-cycle/install methods and bootstrap needs.
- Research pacman/Arch-family semantics and Manjaro differences as a lower-priority target.
- Triage Flatpak, Homebrew/Linuxbrew, pipx and arbitrary Windows installer mechanisms.
- Turn research into backend-specific implementation work only when safe and justified.

## Deliberate boundaries / deferred work

- High-priority: Windows 11 and Debian/Ubuntu Server. Lower priority: Manjaro/Arch, not a substitute for Debian server support.
- macOS is not silently promoted merely because Homebrew research includes it.
- Do not execute AUR build scripts or opaque EXE installers during discovery.

## Related executable tasks

- [`MSHP-PLATFORM-A-010`](../tasks/MSHP-PLATFORM-A/MSHP-PLATFORM-A-010.md)
- [`MSHP-PLATFORM-A-020`](../tasks/MSHP-PLATFORM-A/MSHP-PLATFORM-A-020.md)
- [`MSHP-PKG-RESEARCH-A-010`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-010.md)
- [`MSHP-PKG-RESEARCH-A-020`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-020.md)
- [`MSHP-PKG-RESEARCH-A-030`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-030.md)
- [`MSHP-PKG-RESEARCH-A-040`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-040.md)
- [`MSHP-PKG-RESEARCH-A-050`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-050.md)
- [`MSHP-PKG-RESEARCH-A-060`](../tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-060.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

All actively desired target OS families have proven safe annexation contracts for required app classes, with explicitly deferred or unsupported edge cases.
