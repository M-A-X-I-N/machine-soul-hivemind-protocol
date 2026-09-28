# Runtime annexation architecture

Machine-Soul treats language/runtime lifecycle as a first-class machine capability rather than forcing runtimes into ordinary single-application installation semantics.

## Runtime instance identity

One exact runtime instance preserves:

- runtime subject, such as Python, Node, Lua, or LuaJIT;
- ecosystem version;
- lifecycle backend;
- exact backend instance key;
- architecture;
- flavor/distribution where relevant;
- direct executable and/or installation prefix identity where available.

The backend key is the mutation key. PATH order is never identity.

## Desired installed state is a set

Multiple simultaneously desired versions are normal:

```text
subject: node
backend: nvm-windows-v2
instances:
  - 22.x
  - 24.x
  - 26.x
selected: 24.x
```

The selected/default instance is independent state. Installing a version does not implicitly make it the desired default.

## Backend boundary

Concrete backends implement a small lifecycle contract:

- discover relevant runtime instances;
- discover selected/default backend key;
- install one exact runtime specification;
- uninstall one exact runtime instance;
- select one exact installed instance.

The shared reconciler owns desired-set semantics, provenance, mutation ordering, exact verification, and backend-migration safety. It does not know Python/Node/Lua commands.

This intentionally permits different strategies:

- an official first-party manager;
- a maintained ecosystem version manager;
- Machine-Soul-owned versioned prefixes;
- a future backend not yet selected.

## Ownership and adoption

Runtime ownership is separate from ordinary application package-manager provenance.

Each backend declares its ownership scope. A host-wide backend uses host scope; a per-user manager uses a stable user scope subject. This prevents two accounts on one host from colliding while still allowing machine-owned runtimes to remain account-independent.

Discovery never grants ownership.

If a desired exact runtime already exists but has no matching Machine-Soul runtime provenance, reconciliation refuses it as unmanaged. The instance can be explicitly adopted after exact discovery.

Ownership records preserve enough direct identity to detect drift in version, architecture, flavor/distribution, executable, or prefix.

## Backend migration

A runtime subject owned through one backend cannot be silently reconciled through another backend.

For example, an owned Node set under one version manager is not relabeled as owned by a different manager even if matching Node versions are visible.

The core returns an explicit migration-required condition. A future migration operation must construct/verify target instances and retire old ownership deliberately.

## Reconciliation ordering

For one runtime subject/backend:

1. validate desired/backend identity and ownership;
2. discover exact instances and selected/default state;
3. reject unmanaged desired-instance conflicts or provenance drift;
4. preflight selected-runtime removal safety;
5. install missing desired instances and verify each exact backend key;
6. reconcile selected/default state;
7. remove owned undesired instances exactly;
8. rediscover and verify final installed set and selection.

This means replacing a selected runtime installs/selects the replacement before deleting the old one.

If the currently selected owned instance would be removed and no replacement selection is declared, reconciliation refuses before mutation.

## Healthy multiplicity versus ambiguity

Several different runtime versions are healthy when they have distinct backend keys.

Ambiguity is an unsafe identity collision—for example, one backend returning multiple different instances with the same exact backend key.

This runtime behavior does not weaken ordinary application duplicate-candidate safety.

## Unmanaged observations

A backend may report relevant runtime instances that it does not own, such as legacy/direct installations.

Those instances remain visible but cannot be mutated through the active backend and never become Machine-Soul-owned merely because their version resembles desired state.

## Package-environment extension

Runtime ownership intentionally exposes stable exact runtime-instance identity for the later package-environment layer.

This task does not manage pip/npm/LuaRocks inventories. Package environments will reference exact runtime instances rather than language/version strings.

## Current implementation boundary

The shared runtime core is implemented and supports backend-defined host/user ownership scope. Concrete Python, Node, and Lua/LuaJIT lifecycle backends remain separate concerns.

Machine-Soul therefore has runtime lifecycle semantics before it has ecosystem-specific commands—a deliberate layering boundary.
