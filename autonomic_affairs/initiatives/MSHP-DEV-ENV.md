# MSHP-DEV-ENV — Developer environment annexation

**Status:** OPEN

## Goal

Make Machine-Soul capable of annexing the developer tools, runtimes, version managers, IDEs, editors, and runtime package ecosystems the maintainer actually wants across machines.

Annexation is broader than configuration management. A subject may be useful to manage only for installation/version lifecycle and may have no assimilation directives at all.

## Current state / coverage

Machine-Soul already has generic installation discovery/provenance/scope machinery and independent configuration capabilities. DEV-A has now established the runtime and package-environment architecture; DEV-B is the planned implementation phase.

Completed investigation/synthesis block `MSHP-DEV-A` covers:

- VS Code;
- JetBrains Toolbox and IDE ecosystem;
- Lua/LuaJIT multiversion Windows lifecycle;
- Python multiversion Windows lifecycle;
- Node.js multiversion Windows lifecycle;
- a bounded survey of additional runtimes/toolchains;
- LuaRocks, pip, and npm runtime-bound package ecosystems;
- comparative synthesis and implementation taskification.

## Known gaps

- VS Code and JetBrains Toolbox now have USER-scoped install-only annexation through exact WinGet identities. No selected VS Code desired settings/profile/extension inventory or Settings Sync ownership policy exists yet;
- no selected Toolbox settings, IDE product/version policy, IDE settings/plugins, or Backup-and-Sync ownership policy exists yet, and the Toolbox CLI remains explicitly work-in-progress;
- shared runtime-instance annexation is now implemented by `MSHP-DEV-B-030`: exact desired installed sets, separate selected/default state, backend contracts, host-scoped provenance, explicit adoption, exact removal, and backend-migration refusal. Concrete Python Install Manager, nvm-windows v2, and Lua/LuaJIT backends remain in `MSHP-DEV-B-040..060`;
- runtime provenance is now separate from generic application installation provenance so intentional many-version sets do not weaken ordinary duplicate-install safety;
- LuaRocks research confirms runtime-bound package state needs an explicit environment identity: Lua runtime/version + rocks tree + package inventory. LuaRocks tool installation is separate from any tree inventory; native rocks additionally depend on Lua ABI/header/library and compiler/toolchain compatibility;
- pip research reinforces explicit runtime-bound package environments: deterministic mutation must target an exact interpreter/environment, virtual environments are identities rather than generic scope, externally-managed base interpreters must be respected, and declared desired roots must remain distinct from observed/transitive packages;
- npm research confirms that global package state is prefix/backend/runtime state rather than a universal user or machine scope. Project-local package manifests/locks remain project-owned, while explicitly selected global CLI inventories may be annexable when bound to an exact Node/backend/global-prefix identity;
- package-environment implementation is planned in `MSHP-DEV-B-070..090`: shared exact environment/desired-root ownership semantics, combined pip/npm backends, and a LuaRocks backend.
- Windows native toolchain research is complete and `MSHP-DEV-B-025` now implements exact Visual Studio/Build Tools instance/component discovery, prerequisite queries, explicit instance adoption, and conservative exact-component ownership/reconciliation. Whole-instance provisioning remains blocked on maintainer-selected product/channel/path policy;
- .NET SDK/runtime, Java/JDK, Rust, and Go remain credible future annexation subjects with meaningful multiversion/selection semantics, but current evidence still does not justify executable tasks for them;
- Ruby and PHP remain plausible ecosystem-specific future subjects but are lower priority without a concrete workload; Perl is intentionally cold unless a real dependency appears.

## Deliberate boundaries / deferred work

- Preserve multiversion coexistence as a first-class desired capability where reasonably possible. Represent deliberately desired multiple versions explicitly rather than treating duplicate discovery as ambiguity.
- Keep lifecycle backend-specific behind shared runtime-instance/desired-set/selection concepts: use first-party or ecosystem managers when strong, direct Machine-Soul ownership only when necessary, and do not mandate one cross-runtime manager.
- Investigate first; let evidence decide whether Machine-Soul manages versions directly or delegates to a version manager. Manager identity and manager-switch migration must remain explicit because changing backends can change prefixes, shims, package state, and ownership.
- Do not require assimilation directives for install-only/runtime subjects.
- Treat package-manager tool installation, package-environment lifecycle, and package inventory as separate ownership layers. A package environment may be Machine-Soul-created, explicitly adopted, externally managed/read-only, project-owned, or ephemeral.
- Desired package inventories are first-class only for explicitly managed environments. Keep requested roots separate from transitive/observed packages and preserve manager-native package specifiers where needed.
- Do not invent maintainer configuration or package inventories.
- Do not automatically manage project-local dependency environments. Python virtual environments, requirements/lock files, Node `package.json`/lockfile state, and similar project dependency state remain project-owned unless an environment is explicitly adopted.
- Do not use pip overrides such as `--break-system-packages` as normal reconciliation policy for externally managed Python interpreters; respect external ownership boundaries.
- Do not treat npm `-g` as a machine-global scope. Resolve and preserve the exact Node/backend/global prefix before owning global package inventory, and keep registry credentials/tokens outside tracked desired state.
- Runtime removal/migration must account for owned package environments bound to that runtime before deleting or reassigning the runtime. Never transfer environment ownership merely because observed package names match.
- Do not promote every common language/toolchain into executable work merely because it exists.
- Treat Visual Studio/Build Tools instance identity, exact MSVC/SDK component identity, and derived build-session selection as separate layers. Machine-Soul may own exact components only in an explicitly adopted instance and must preserve unowned components. Keep .NET/JDK/Rust/Go as structured initiative gaps until concrete demand promotes them.
- Keep Ruby/PHP/Perl deferred unless a real workload makes their lifecycle worth owning.
- VS Code extensions and JetBrains plugins justify a future host-bound add-on inventory concept, but do not implement it until desired add-ons/host/profile ownership are selected.
- Coordinate configuration-specific findings with `MSHP-WIN-CONFIG` instead of duplicating desired-state ownership.

## Related executable tasks

`MSHP-DEV-A-010` through `MSHP-DEV-A-120` form the completed investigation/synthesis block. `MSHP-DEV-B-010` through `MSHP-DEV-B-100` (including inserted `MSHP-DEV-B-025`) form the planned implementation/research phase. Mutable state and dependencies remain authoritative in [`../agent_tasks.md`](../agent_tasks.md).

## Promotion / closure criteria

Promote implementation work only when an investigation identifies a safe bounded capability and any required maintainer-selected desired state is available.

This initiative may remain OPEN while current runtime/editor implementations are complete if future developer-environment subjects remain intentionally desired but deferred.
