# Shared Python core implementation

V2-58 implemented the generic Python runtime; V2-60/V2-61 subsequently made it authoritative and retired the parallel shell/PowerShell policy runtime.

Important reuse/debugging facts:

- Python `os.symlink` passed the real hosted-Windows lifecycle tests; do not retain PowerShell symlink creation unless a different proven environment requires a primitive.
- Windows `os.readlink` can return NT substitution paths (extended `\\?\` form). Normalize equivalent DOS/UNC/extended spellings before comparing link identity.
- Deployment-state identity is keyed from the logical declared destination, not whatever alternate spelling a platform API returns after inspection.
- New config/install state is JSON, but readers intentionally retain compatibility with the legacy Linux line/base64 format and legacy platform hash paths so pre-migration ownership/backup state remains recoverable.
- Apply owns per-target backup/restore/verification and checkout-relocation repair; multi-file apply rolls back earlier changed targets when a later target fails.
- A correct-looking expected symlink without ownership state is not enough for Python Unapply; it reports `ownership_unproven` instead of deleting it.
- Apt and WinGet are shared strategy handlers. Pre-existing installs remain unmanaged and are never silently claimed for uninstall.
- Native process invocation now exists through the v1 protocol, but no current legacy helper is grandfathered into primitive status.
- V2-61 retired the legacy policy/forwarding scripts after parity. Remaining shell/PowerShell under `autonomic_affairs/tests/` are harnesses, not production runtime.
