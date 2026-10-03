# pip annexation findings

Durable findings from `MSHP-DEV-A-090` (2026-09-28):

- pip mutation must target an exact Python environment. Prefer the environment/interpreter's exact `python -m pip`; activation and PATH are convenience, not identity.
- Treat virtual environments as package-environment identities, including root/path and interpreter relationship. Do not silently annex arbitrary project venvs.
- Respect `EXTERNALLY-MANAGED` base interpreters; overriding external ownership is not normal reconciliation policy.
- Base-runtime, user-site, and venv package state are distinct. User-site and mutable runtime-global inventories should be explicitly adopted rather than default Machine-Soul state.
- `pip list --format=json` and `pip inspect` provide machine-readable discovery; `pip freeze` is an installed-state snapshot in requirements syntax, not desired-root provenance or a lockfile.
- Keep declared desired roots separate from observed/transitive dependencies. `pip list --not-required` is diagnostic, not ownership provenance.
- Project requirements and lock files normally remain project-owned. Do not ingest them into global machine state automatically.
- pip itself is separate environment/tool state from the packages it manages.
- Source builds use isolated temporary build environments by default and may require native compilers/headers/libraries; report those as prerequisites rather than silently annexing toolchains.
- Index credentials may live in URLs, netrc, or keyrings. Never store credentials/tokens in tracked Machine-Soul configuration.
- When a venv sees system site packages, distinguish environment-local installed packages from inherited visible packages.

Detailed research lives in `autonomic_affairs/tasks/archive/MSHP-DEV-A/workspace/pip.md`.
