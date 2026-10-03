# Runtime package-environment synthesis findings

Durable findings from `MSHP-DEV-A-110` (2026-09-28):

- LuaRocks, pip, and npm justify a shared **package environment** concept, not a universal package-manager command abstraction.
- Package-manager tool installation, environment lifecycle, and package inventory are separate ownership layers.
- Exact environment identity is backend-specific but must be stable: LuaRocks tree, Python interpreter/venv/site environment, npm Node/backend/global-prefix context.
- Runtime-bound environments reference exact runtime-instance provenance from the runtime model; version strings alone are insufficient.
- Desired package inventory is an optional first-class capability per explicitly managed environment.
- Persist declared **desired roots** separately from observed/transitive dependency closure. Preserve manager-native requirement/package specifiers where semantics matter.
- Environment ownership needs conservative states such as Machine-Soul-created, explicitly adopted, externally-managed/read-only, project-owned, and ephemeral.
- Unknown/unowned top-level packages in an adopted environment are reported and preserved by default; absence from desired roots is not deletion authorization.
- Project-local dependency environments remain project-owned unless explicitly adopted.
- Runtime deletion/manager migration must reconcile bound owned package environments before the runtime/backend disappears.
- Credentials/tokens remain outside tracked state; native build toolchains are prerequisites, not silent package side effects.
- Final implementation taskification is deliberately deferred to `MSHP-DEV-A-120` so runtime and package-environment primitives/backends can be sequenced as one roadmap.

Detailed synthesis lives in `autonomic_affairs/tasks/MSHP-DEV-A/workspace/package_environment_synthesis.md`.
