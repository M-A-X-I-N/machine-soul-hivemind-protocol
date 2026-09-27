# Legacy runtime migration audit

V2-57 mapped the shell/PowerShell implementation to the Python architecture. Canonical detail is in `autonomic_affairs/docs/LEGACY_MIGRATION_MAP.md`.

High-value conclusions:

- do not mechanically port shell/PowerShell code;
- root/host/account/state/symlink/config/install policy becomes generic Python;
- Fish apt and OMP WinGet become declared strategies + shared handlers;
- ordinary app manage/forwarder scripts become declarations + uniform wrappers;
- OMP account-specific source selection becomes shared config precedence;
- CMD remains an initial application-specific composite hook using generic config lifecycle plus a Python Windows-registry helper;
- Windows Terminal/PowerShell/compatibility-shell destinations need reusable destination strategies/helpers rather than wrapper logic;
- no existing native script is automatically justified as a future primitive merely because it is native today;
- retain legacy state/provenance read compatibility until backups/ownership lineage are safely migrated;
- preserve behavior tests, not legacy implementation chains;
- stale `TASKS.md` root search and concrete-machine adapter fallbacks are deletion targets.

V2-58 builds alongside legacy code. Retirement belongs later after parity.
