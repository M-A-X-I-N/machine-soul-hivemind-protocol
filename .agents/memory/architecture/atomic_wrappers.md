# Atomic wrapper contract

Canonical detail: [`../../../autonomic_affairs/docs/ATOMIC_WRAPPERS.md`](../../../autonomic_affairs/docs/ATOMIC_WRAPPERS.md).

V2-53 decisions:

- final Python wrappers live directly under `annexation/<application>/`, not per-platform subdirectories;
- `_application.py` is the non-executable declaration; unprefixed operation files are atomic executable/importable interfaces;
- file presence is not capability truth; platform capability comes from the declaration;
- `run(context=None)` is the canonical semantic path and returns the common result;
- `main(argv=None)` is only shared CLI/context/presentation/exit adaptation;
- importing a wrapper is non-mutating;
- direct execution uses the one repository-root `sys.path` bootstrap;
- wrappers contain no package/config/state/account/platform/orchestration logic;
- orchestrators call wrapper `run(...)`, keeping direct and composed execution on one path.
