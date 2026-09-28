# Runtime and version-management synthesis

Status: completed synthesis output for `MSHP-DEV-A-070`.

Research/synthesis date: 2026-09-28.

## Conclusion

The Lua, Python, and Node investigations justify a **shared runtime annexation model**, but they do **not** justify one universal runtime manager.

The shared model is:

1. a runtime subject can have multiple exact installed runtime instances;
2. the desired installed state is therefore a **set**, not one scalar version;
3. selected/default command resolution is independent desired state;
4. each instance records the backend/manager that owns its lifecycle;
5. discovery and uninstall address an exact runtime instance rather than whichever executable wins PATH;
6. architecture/flavor/distribution identity is part of instance identity when the ecosystem exposes it;
7. project-local selection normally remains project-owned state rather than Machine-Soul global state.

Backend behavior stays runtime-specific.

## Evidence matrix

| Concept | Lua | Python | Node | Shared? |
|---|---|---|---|---|
| Multiple desired installed versions | Strongly required | Native manager capability | Normal/important | **Yes** |
| Separate global/default selection | Required | Native `default_tag` | Manager-native/default/shim | **Yes** |
| Exact version-instance uninstall | Required | Native manager command | Manager-native | **Yes** |
| Architecture/flavor in identity | x86/x64, Lua vs LuaJIT | platform/free-threaded/distributor tags | architecture/version | **Yes** |
| Backend/manager identity | direct/Scoop/build possibilities | official Python Install Manager | nvm-windows/fnm/Volta/mise possibilities | **Yes** |
| Project-local version selection | Usually external | project files/launcher semantics | `.nvmrc`, `.node-version`, package metadata | **Yes, but normally project-owned** |
| One universal manager | No clean Windows Lua answer | unnecessary; strong first-party manager | several good choices | **No** |
| One universal install scope | No | user-scoped official manager | often user-scoped, backend dependent | **No** |

## Runtime instance identity

A discovered or desired runtime instance needs enough identity to remain exact across coexistence and uninstall.

Conceptually:

```text
runtime_subject
runtime_version
flavor_or_distribution
architecture
backend
backend_instance_key
install_scope
prefix_or_executable_identity
ownership
```

Not every ecosystem fills every field. The model should permit absent/not-applicable dimensions rather than manufacture values.

Examples:

- Lua 5.4 x64 from a Machine-Soul-owned versioned prefix;
- LuaJIT 2.1 x64 from a different backend;
- Python manager tag `3.14`;
- Python free-threaded/platform-qualified manager tag;
- Node 24.x owned by nvm-windows v2.

The stable backend instance key is more important than a pretty display version for mutation safety.

## Desired installed set

Current single-package installation semantics are insufficient for runtimes where several versions are intentionally desired.

The model should be capable of expressing:

```text
desired runtimes:
  lua:
    instances: [5.1, 5.4, 5.5, luajit-2.1]
    selected: 5.4
  python:
    instances: [3.13, 3.14]
    selected: 3.14
  node:
    instances: [22, 24, 26]
    selected: 24
```

The exact configuration syntax is not chosen here.

The key semantic distinction is:

- **unmanaged duplicate discovery** can still be ambiguous/conflicting;
- **multiple explicitly desired owned instances** are healthy state.

Generic provenance/discovery therefore needs a way to distinguish intentional multiplicity from accidental candidate duplication.

## Selected/default state

Selection is not implied by installation order or PATH precedence.

A runtime backend may implement selection using:

- manager configuration;
- manager-native shims;
- a Machine-Soul-owned shim/alias layer;
- another runtime-specific mechanism.

Shared orchestration should ask the backend to reconcile selection; it should not encode Python `default_tag`, nvm commands, or Lua shim rules into the common model.

If the selected instance is removed, reconciliation must either:

1. atomically select another explicitly desired instance; or
2. refuse the removal while desired selected state would become invalid.

## Backend delegation

The correct reusable abstraction is **backend delegation**, not one cross-runtime manager.

Backend examples:

- Python → official Python Install Manager;
- Node → likely nvm-windows v2 or fnm after final roadmap choice;
- Lua → direct/versioned-prefix or acquisition-backed ownership may be necessary;
- future Rust → likely `rustup`;
- future .NET/JDK/Go → ecosystem-specific lifecycle.

A backend contract should eventually cover only common orchestration needs:

- discover managed and relevant unmanaged instances;
- normalize exact instance identity;
- install/reconcile desired instances;
- remove one exact owned instance;
- inspect/reconcile selected/default state where supported;
- report backend-specific conflicts/unsupported semantics.

It should not require every backend to expose identical package-manager commands or filesystem layout.

## Manager switching

Changing a runtime from one backend to another is not an ordinary update.

A manager switch may change:

- installation prefixes;
- shims/PATH behavior;
- package/global-tool state;
- ownership provenance;
- supported architectures/flavors;
- selected/default configuration.

Therefore backend identity is part of durable ownership and a future manager switch should be an explicit migration/adoption operation, not automatic reconciliation.

## Discovery and provenance evolution

Existing installation discovery/provenance was designed around one application/package candidate per owned install scope. Runtime multiversion support needs an additional layer rather than weakening ambiguity safety globally.

A future implementation should preserve:

- generic package-manager provenance for installing the **manager/tool** itself;
- runtime-instance provenance for versions owned **through** that manager/backend;
- exact backend instance keys and direct verification;
- unmanaged runtime candidates that remain visible but unowned;
- explicit desired multiplicity.

This avoids teaching every ordinary application that duplicate package candidates are acceptable.

## Scenario walkthroughs

### Several desired versions

Desired Python 3.13 + 3.14 or Node 22 + 24 + 26 is healthy when each exact instance is owned and discovered. No ambiguity should be raised merely because there are several versions.

### Selected/default version changes

Changing selected Node 24 → 26 should mutate selection only. It should not reinstall both runtimes or change package ownership.

### Uninstall one version

Removing Lua 5.1 must target only its exact runtime instance/prefix. Other Lua versions and LuaJIT remain untouched.

If 5.1 is selected/default, selection must be reconciled first or the operation fails safely.

### Manager switch

Moving Node from fnm → nvm-windows is a migration. Existing versions cannot simply be relabeled as owned by the new backend.

## Additional-runtime compatibility

The survey does not reveal a contradiction:

- Rust's `rustup` maps naturally to installed toolchain set + default/override + backend identity.
- .NET has separate installed SDK/runtime sets and project-local selection.
- JDKs require version + vendor/distribution + ambient default.
- Go supports explicit side-by-side versions.
- MSVC/Visual Studio toolsets are more complex, but still reinforce exact coexisting toolchain instances plus project selection.

The model should remain generic enough to support these later without pretending their lifecycle is identical.

## Implementation timing decision

Do **not** create runtime implementation tasks in this task.

The shared runtime model is now justified, but the immediately following LuaRocks/pip/npm investigations intentionally test how runtime-bound package environments interact with runtime instances, updates, and removal. Creating implementation tasks before `MSHP-DEV-A-110` would risk freezing the boundary one task too early.

`MSHP-DEV-A-120` remains the right place to produce bounded implementation tasks using both runtime and package-environment synthesis.

This is a deliberate no-task decision, not missing taskification.

## Architectural decision

Machine-Soul should eventually add:

- first-class desired runtime-instance sets;
- runtime-instance discovery/provenance separate from generic package-manager install provenance;
- selected/default runtime state as a separate concern;
- runtime lifecycle backend interfaces;
- explicit backend identity/migration boundaries.

Machine-Soul should **not** add:

- one universal version-manager requirement;
- one global runtime install scope;
- PATH order as selected-version policy;
- automatic ownership transfer between runtime managers;
- project-local version-file ownership as part of global machine annexation.
