# Windows configuration candidate findings

Durable findings from `MSHP-APPS-A-010` (2026-09-28):

- Windows Terminal is already managed and remains the file-config baseline.
- WinGet client `settings.json` is a strong per-user config candidate; packaged path is under `Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\LocalState`, while source-built WinGet uses `%LOCALAPPDATA%\Microsoft\WinGet\Settings`. Keep user settings distinct from administrator settings, sources, package export/import, and WinGet Configuration/DSC.
- WSL `%UserProfile%\.wslconfig` is a strong singleton file candidate for global WSL2 VM settings. Changes require WSL restart/shutdown; not every property has a generic runtime verifier.
- Windows OpenSSH client `%UserProfile%\.ssh\config` is a strong singleton file candidate. Never include keys, `known_hosts`, credentials, sockets, or generated host state in the same managed config boundary.
- PowerToys should use its supported `PowerToys.DSC.exe`/Microsoft DSC get/set/test/export surface rather than symlinking internal AppData JSON. Canonical desired module state is still needed.
- Windows Sandbox `.wsb` files are multiple launch profiles/assets, not one singleton app config.
- Explorer/Advanced Windows Settings are OS registry/policy desired state, not ordinary application config.
- Notepad currently lacks a supported ordinary settings contract; do not manage opaque package LocalState/session blobs.

Strong candidates are intentionally not executable yet because their canonical desired content has not been supplied. They are tracked in `meta/initiatives/MSHP-WIN-CONFIG.md`.

Detailed sources/matrix live in `meta/tasks/archive/MSHP-APPS-A/workspace/windows_config_candidates.md`.
