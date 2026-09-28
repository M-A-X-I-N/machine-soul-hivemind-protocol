# Python multiversion annexation findings

Durable findings from `MSHP-DEV-A-040` (2026-09-28):

- The official Python Install Manager is now the preferred Windows runtime manager direction; traditional executable installers are transitional and planned to stop with Python 3.16.
- The manager natively supports multiple exact runtime tags, machine-readable `list` formats, `--only-managed`, exact install/uninstall, architecture/flavor tags, and a separate configurable default runtime.
- Managed runtimes are per-user only. Machine-Soul should initially embrace USER scope rather than inventing system-wide Python management.
- Scripted automation should prefer `pymanager` over ambiguous `py` because the legacy launcher may occupy `py`.
- `%AppData%\Python\pymanager.json` is a documented user config surface; `default_tag` gives native default-selection semantics.
- Manager-owned versus unmanaged runtimes are explicitly distinguishable, fitting Machine-Soul discovery/ownership.
- Updating/replacing managed runtimes removes modifications/global packages inside that runtime, so package inventories must remain a separate later decision.
- uv, pyenv-win, and mise remain useful alternatives, but the official manager is the strongest host-level Windows CPython annexation backend unless cross-runtime synthesis finds a compelling shared-manager reason otherwise.

Detailed research lives in `autonomic_affairs/agent_tasks/MSHP-DEV-A/workspace/python_multiversion.md`.