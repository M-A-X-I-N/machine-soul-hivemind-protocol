# Runtime package-environment synthesis

Status: completed synthesis output for `MSHP-DEV-A-110`.

Synthesis date: 2026-09-28.

## Conclusion

LuaRocks, pip, and npm justify reusable **package-environment** and **desired package inventory** concepts.

They do **not** justify one universal package-manager command model.

The common architecture is:

1. package-manager tool installation is separate from package environments;
2. every managed package environment has an exact identity;
3. runtime-bound environments reference the exact runtime/backend instance they belong to;
4. desired inventory is a set of explicitly requested **root packages**;
5. transitive/observed packages are environment state, not independently desired roots;
6. environment lifecycle/ownership is separate from inventory ownership;
7. mutation stays manager-native behind a shared orchestration contract;
8. project-local and ephemeral environments are unowned by default;
9. credentials/secrets are never part of tracked package desired state;
10. native-build/toolchain requirements are prerequisites, not packages to silently annex.

## Evidence matrix

| Concept | LuaRocks | pip | npm | Shared? |
|---|---|---|---|---|
| Tool install separate from managed packages | Yes | Yes | Yes | **Yes** |
| Exact environment locator | rocks tree | interpreter/venv/site environment | global/local prefix/project root | **Yes** |
| Runtime binding matters | Lua runtime/ABI | exact Python environment | Node/backend/prefix | **Yes** |
| Explicit desired roots | needed | needed | needed | **Yes** |
| Transitive closure distinct from desired roots | Yes | Yes | Yes | **Yes** |
| Machine-readable inventory | list/porcelain | list/inspect JSON | ls JSON | **Yes, backend-specific** |
| Exact native install/uninstall | manager-native | manager-native | manager-native | **Yes, backend-specific** |
| Project-local env exists | project tree | venv/project lock | package root/node_modules | **Yes; normally project-owned** |
| External/read-only ownership boundary | arbitrary/unadopted trees | EXTERNALLY-MANAGED | unadopted project/prefix/backend state | **Yes as generic ownership state** |
| One universal scope model | No | No | No | **No** |
| One universal lock/export format | No | No | No | **No** |

## Package environment identity

A shared environment identity needs to preserve enough information for exact discovery and mutation without flattening backend semantics.

Conceptually:

```text
package_environment_id
manager_kind
manager_instance/tool identity
runtime_instance_ref?       # required when runtime-bound
environment_kind
environment_locator
ownership_state
mutation_policy
```

Examples:

- Lua 5.4 runtime + `C:\...\lua54\rocks`;
- Python venv at `C:\projects\x\.venv` with exact environment Python;
- explicitly adopted Python user-site environment for Python 3.14;
- Node 24 under nvm-windows + the resolved npm global prefix;
- project-local npm root — discovered if asked, but project-owned by default.

The environment locator is backend-specific:

- LuaRocks tree root;
- Python environment interpreter/root/site scheme;
- npm prefix/project root.

Do not invent one filesystem-layout field that pretends these are identical.

## Environment ownership states

The evidence supports distinguishing at least these semantics:

### Machine-Soul-created

Machine-Soul owns the environment lifecycle and may safely reconcile its desired package inventory.

Examples could later include a dedicated Python tool venv or a Machine-Soul-created LuaRocks tree.

### Explicitly adopted

The environment existed already, but the human explicitly chose to place its package inventory under Machine-Soul management.

Adoption needs a baseline/reconciliation policy; it is not implied by discovery.

### Externally managed / read-only

Machine-Soul may discover/report the environment but must not mutate it under normal reconciliation.

Python's `EXTERNALLY-MANAGED` marker is the clearest ecosystem-native example.

### Project-owned

The environment is controlled by project files/workflows.

Examples:

- Python project venv + requirements/lock;
- npm package.json/package-lock/node_modules;
- LuaRocks project tree.

Global Machine-Soul annexation does not silently claim these.

### Ephemeral

Temporary build environments, caches, resolver sandboxes, and similar short-lived state are not desired package environments.

Examples include pip's isolated build environments.

## Runtime reference

A runtime-bound package environment must reference the **exact runtime instance**, not merely a language/version string.

Why:

- Lua native modules depend on Lua ABI/flavor/architecture;
- Python venvs/interpreter sites bind to a concrete interpreter environment;
- npm global state can be tied to a Node manager/runtime/prefix.

Conceptually:

```text
runtime_instance_ref -> package_environment
```

not:

```text
language = "python"
version = "3.14"
```

The stable runtime/backend instance identity from `MSHP-DEV-A-070` should be the foreign-key-like anchor.

A manager may expose an environment that is not strictly tied to one runtime instance. The model should permit `runtime_instance_ref` to be absent when genuinely not applicable rather than manufacturing a fake runtime.

## Desired root inventory

Desired package inventory should be a first-class **optional capability per explicitly managed environment**.

Conceptually:

```text
desired_roots:
  - manager-native package requirement/specifier
  - optional normalized package identity
  - optional policy/version constraint
```

Machine-Soul should persist what the human actually requested, not reverse-engineer desired state from an installed dependency tree.

Observed state should distinguish:

- desired root package;
- installed root package;
- transitive dependency;
- unmanaged top-level package;
- missing/conflicting package;
- environment/tooling problem.

## Preserve manager-native package semantics

A shared model should not reduce every package request to `name == exact-version`.

Examples of meaningful backend-native semantics include:

- LuaRocks rock version/revision and namespace;
- Python requirement specifiers, extras, direct URLs/editables;
- npm scopes, semver ranges, tags and package specs.

A normalized package name can support comparison/display, but the original manager-native desired specifier must remain available for mutation and intent fidelity.

## Discovery

Shared orchestration can require a backend to return normalized environment/package observations, but raw commands remain backend-specific.

Examples:

- LuaRocks: runtime/tree-qualified `list --porcelain`;
- pip: exact environment `pip inspect` / `pip list --format=json`;
- npm: exact backend/prefix `npm ls -g --depth=0 --json`.

Discovery must be performed **inside the identified environment**.

Never run whichever package manager is first on PATH and attach the result to a desired environment afterward.

## Reconciliation

A shared reconciliation loop can conceptually:

1. resolve the exact environment and confirm mutation is allowed;
2. discover observed roots/dependency state;
3. compare against declared desired roots;
4. invoke backend-native install/update/remove operations;
5. rediscover and verify;
6. update provenance for owned desired roots/environment state.

The backend owns:

- command syntax;
- dependency resolver behavior;
- install/uninstall mechanics;
- package-spec parsing;
- environment-specific configuration.

The shared layer owns:

- environment identity;
- authorization/ownership;
- desired-root intent;
- runtime dependency ordering;
- provenance and verification discipline.

## Unmanaged top-level packages

An explicitly managed environment can still contain packages that Machine-Soul did not install.

Do not automatically delete them just because they are absent from desired roots unless the environment has been explicitly placed into an **exclusive/convergent** ownership mode.

Initial behavior should be conservative:

- desired roots are ensured present;
- Machine-Soul-owned roots removed from desired state may be removed safely;
- unknown/unowned roots are reported but preserved.

A future stricter “environment entirely owned by Machine-Soul” mode can be separate policy.

## Tool ownership

Installing the package-manager tool and managing packages through it are independent capabilities.

Examples:

- LuaRocks tool may be installed while no rock tree is adopted;
- pip may be bundled in one Python environment and absent/upgraded in another;
- npm ships with Node but can be upgraded independently.

Package reconciliation should first verify a compatible tool is available for that environment/backend rather than mutating tool versions implicitly.

## Environment lifecycle versus package inventory

Creating/deleting an environment is not the same operation as reconciling its packages.

For example:

- create a Python venv;
- then reconcile desired packages in it.

Or:

- create/assign a LuaRocks tree;
- then install roots.

npm global-prefix environments may be supplied by the Node/backend rather than independently created.

Shared architecture should therefore expose environment discovery/lifecycle separately from inventory reconciliation even where a backend combines them internally.

## Runtime deletion and migration

Runtime lifecycle depends on package-environment state.

Before removing an owned runtime instance:

1. enumerate package environments bound to it;
2. determine whether any have desired owned roots;
3. migrate/recreate those environments on a replacement runtime if desired;
4. or explicitly retire their desired state;
5. only then remove the runtime.

Never leave desired package inventory pointing at a deleted runtime.

Manager switching follows the same principle: create/resolve target environments, reapply desired roots, verify, then retire old owned state.

Observed package-name equality is not ownership migration.

## User/global/package scopes

“Global” and “user” are backend terms, not universal scope identities.

- LuaRocks user/global/tree semantics are tree-driven.
- pip user site differs from base interpreter and venv environments.
- npm global is the configured prefix for the selected npm/backend context.

The shared model should store an **environment kind/classification for policy and display**, but exact mutation identity comes from backend/runtime/environment locator, not from a universal enum such as `GLOBAL`.

## Project-local environments

Project-local dependencies remain out of global Machine-Soul annexation by default.

Machine-Soul may eventually offer explicit project-environment construction, but that should consume the project's own dependency declarations/locks rather than copy them into machine-wide configuration.

Examples:

- `pylock.toml`, requirements, project metadata;
- `package.json` / package-lock;
- Lua rockspec/project trees.

The project repository remains source of truth.

## Secrets and registry configuration

All three ecosystems can need remote repositories/indexes and credentials.

The shared architecture should distinguish:

- portable non-secret source/index/registry configuration;
- secret authentication material;
- machine-local credential-provider configuration.

Secrets must never enter tracked desired package state, provenance, logs, or `.agents/`.

Backends should support redaction/safe diagnostics where command output could expose registry URLs containing credentials.

## Native-build prerequisites

Package installation can require external build prerequisites:

- compiler/toolchain;
- headers/libraries;
- architecture-compatible native dependencies;
- Python/build-system helpers;
- Node native-addon tooling;
- Lua ABI-compatible libraries.

These are **prerequisites**, not transitive package roots to silently annex.

A backend may report structured prerequisite failures, but package reconciliation should not make arbitrary system-wide toolchain choices.

This reinforces the need for the future MSVC/Build Tools investigation.

## Scenario walkthroughs

### Two Lua versions, two rock trees

Each tree has its own environment identity and runtime reference. Installing a desired root into Lua 5.4 does not mutate Lua 5.5.

### Two Python runtimes plus a project venv

Python 3.13 and 3.14 runtime environments are distinct. A project `.venv` is project-owned unless explicitly adopted. An externally-managed system Python stays read-only.

### Node 22 and 24 under a manager

Each backend/runtime/prefix context can expose global package state. Changing selected Node does not transfer package ownership.

### Unknown packages in an adopted environment

Machine-Soul ensures its declared roots and reports unknown roots. It does not delete unknown packages by default.

### Runtime removal

If a runtime has an owned package environment with desired roots, runtime removal must first reconcile/migrate/retire that environment.

## Implementation timing decision

Do **not** create separate implementation tasks inside this synthesis checkpoint.

The architecture is now justified, but `MSHP-DEV-A-120` is explicitly the final developer-annexation roadmap synthesis and has the complete evidence set across editors, runtimes, and package environments.

Creating implementation tasks here would split roadmap ownership and risk duplicate sequencing.

This is a deliberate bounded decision: `MSHP-DEV-A-120` should taskify the shared runtime/package-environment primitives and the concrete first backends together.

## Architectural decision

Machine-Soul should eventually support:

- explicit package-environment identity;
- exact runtime-instance references;
- environment ownership/adoption/mutation policy;
- optional desired root inventories per managed environment;
- observed/transitive package discovery;
- backend-specific package lifecycle strategies;
- runtime↔environment lifecycle dependency ordering;
- secret-safe source/auth boundaries.

Machine-Soul should **not** introduce:

- one universal package-manager command vocabulary;
- machine-global package inventories detached from environments;
- automatic project dependency ownership;
- automatic deletion of unknown packages in merely adopted environments;
- tracked registry/index credentials;
- package-manager side effects that silently choose/install native system toolchains.
