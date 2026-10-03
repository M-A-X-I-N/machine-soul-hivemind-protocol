# Windows installation scope findings

Durable findings from `MSHP-INST-A-020` (2026-09-28).

- WinGet supports `--scope user|machine` on install and scope filtering on list/uninstall/upgrade.
- WinGet settings distinguish `preferences.scope` (ordering/fallback) from `requirements.scope` (filter/fail). Ambient preferences must not define Machine-Soul scope.
- WinGet manifests may provide user and machine installer nodes. Elevation requirement is a different dimension from install scope.
- Current MSHP WinGet mutation/discovery is unscoped and therefore insufficient for dual-scope ownership.
- MSI has real per-user/per-machine contexts; current HKCU/HKLM ARP discovery handles current-user versus machine but not complete other-user inventory.
- AppX/MSIX installed packages are user-profile registrations. Provisioned packages for future users are a separate image concept, not ordinary `MACHINE` scope.
- Non-current-account user-scoped mutation is unsupported until a proven target-user execution mechanism exists.
- Current OMP WinGet manifest 31.3.0 is AppX/MSIX and omits manifest `Scope:`; use it as a validation/regression case for explicit `--scope user` plus native PACKAGE_USER verification.

Detailed sources/scenarios live in `autonomic_affairs/tasks/MSHP-INST-A/workspace/windows_scope.md`.
