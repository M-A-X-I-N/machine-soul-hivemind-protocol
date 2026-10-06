# Package-environment annexation architecture

Machine-Soul treats runtime package state as an explicitly owned **package environment**, not as a machine-global package list.

## Exact environment identity

Each environment preserves:

- package manager and backend identity;
- an exact backend key;
- a backend-specific locator such as an interpreter, prefix, or rocks tree;
- a descriptive classification that does not pretend backend-specific scopes are universal;
- an optional exact runtime-instance reference, including runtime backend key and ownership scope when relevant.

This permits several package environments for the same runtime or manager without relying on PATH or ambient selection.

## Ownership and mutation

Observed environments are conservative by default. Machine-Soul can record an environment as:

- Machine-Soul-created;
- explicitly adopted;
- externally managed/read-only;
- project-owned;
- ephemeral/unmanaged;
- otherwise unmanaged.

Only Machine-Soul-created or explicitly adopted environments may receive mutable ownership policy. The normal mutable policy is **managed roots**: Machine-Soul ensures and owns only declared desired roots and preserves unknown top-level packages. A stronger **exclusive** policy exists only as an explicit opt-in. Read-only policy remains available even for an owned environment.

Project and externally managed environments are never silently adopted.

## Desired roots versus observed packages

Desired package state records manager-native root specifiers separately from observed inventory.

A backend verifies each desired root and maps it to an exact observed package identity plus the exact manager-specific removal identity. This lets the shared layer own and later remove a root without inventing a common package-specification language.

Observed transitive dependencies remain observations. They do not become desired roots merely because they are installed.

## Backend contract

Concrete backends own:

- exact environment discovery;
- manager-tool availability checks;
- environment-local inventory discovery;
- manager-native verification of desired root semantics;
- install/update/remove commands.

The shared core owns:

- environment ownership/provenance;
- desired-root intent;
- unknown-root preservation/exclusive policy;
- mutation authorization;
- rediscovery/verification discipline;
- safe runtime dependency ordering.

Package-manager tool installation remains a separate capability from environment/package reconciliation.

## Runtime dependency ordering

A runtime may not be removed while a Machine-Soul-owned package environment remains bound to that exact runtime instance. The package layer exposes a runtime-removal guard; the runtime reconciler accepts generic dependency guards rather than importing package policy directly.

This keeps the runtime core independent while allowing package environments to block unsafe removal before any runtime mutation occurs.

## Secret boundary

Tracked desired package state and package-environment provenance reject obvious credential-bearing values, including credential-bearing URLs. Backend operation diagnostics are redacted before shared orchestration exposes them.

Credentials, registry tokens, index authentication, and raw backend output are not package desired state and are never intentionally persisted by the shared package-environment core.

## Concrete backends

The shared core remains manager-agnostic; concrete backends preserve their own command and environment semantics.

### pip exact environments

The initial pip backend manages only explicitly enumerated Python environments. Every operation is bound to an exact interpreter and invokes pip through that interpreter rather than a PATH-selected executable.

Environment identity records the interpreter, prefix, and exact runtime reference. Discovery distinguishes ordinary runtime-global/venv environments from project-owned, ephemeral, and externally-managed Python environments. Project-owned and externally-managed environments remain non-adoptable under normal policy.

Inventory uses pip's local machine-readable inspection so inherited system-site visibility is not mistaken for locally owned package state. Requested roots remain distinct from transitive packages. If pip's resolver considers a desired root satisfied only through inherited visibility, reconciliation forces a local installation before the root can become owned.

### npm runtime-global prefixes

The initial npm backend binds global package state to an exact Node runtime plus its resolved global prefix. It invokes the npm CLI through the exact Node executable/runtime rather than ambient PATH and never interprets `-g` as machine-global state.

Each runtime/global-prefix pair is a separate package environment. Machine-readable npm inventory distinguishes top-level global roots from observed transitive dependencies, allowing simultaneous Node versions to carry different global CLI inventories safely.

Project `package.json`, lockfiles, and local `node_modules` remain project-owned and outside this backend.

### LuaRocks exact runtime/tree environments

The initial LuaRocks backend binds each managed tree to one exact owned Lua/LuaJIT runtime instance plus one exact physical rocks-tree root. It invokes LuaRocks with explicit Lua directory, Lua line, tree, no-project, and single-tree dependency-mode selectors rather than ambient PATH or project discovery.

Distinct simultaneous Lua runtimes use distinct trees. One physical tree is refused when configured against different exact runtimes. Project-local trees remain project-owned and non-adoptable by default.

Porcelain inventory remains tree-local. Desired roots are manager-native package/version pairs; observed dependencies remain transitive observations rather than independently owned roots. Exact removal identities include package and installed version so reconciliation cannot remove a same-named rock from another runtime/tree.

LuaRocks itself remains a separate tool capability. Native rock failures caused by missing Lua headers/libraries, compilers, or external dependencies are surfaced explicitly rather than silently annexing a native toolchain.

### Shared safety properties

The concrete pip, npm, and LuaRocks backends preserve manager-native desired specifiers, keep tool availability separate from package-root ownership, preserve unknown top-level packages under managed-root policy, keep project-owned environments outside implicit annexation, bind mutation to exact runtime/environment identity, and report missing native-build prerequisites instead of silently annexing compilers or SDKs.

Secret-bearing desired state remains rejected/redacted according to the shared package-environment boundary.
