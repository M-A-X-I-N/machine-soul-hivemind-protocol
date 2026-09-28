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

The shared core deliberately contains no pip, npm, or LuaRocks command syntax. Those ecosystems validate the abstraction in later DEV-B tasks while preserving their distinct interpreter/prefix/tree semantics.
