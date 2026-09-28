# MSHP-DEV-ENV — Developer environment annexation

**Status:** OPEN

## Goal

Make Machine-Soul capable of annexing the developer tools, runtimes, version managers, IDEs, editors, and runtime package ecosystems the maintainer actually wants across machines.

Annexation is broader than configuration management. A subject may be useful to manage only for installation/version lifecycle and may have no assimilation directives at all.

## Current state / coverage

Machine-Soul already has generic installation discovery/provenance/scope machinery and independent configuration capabilities. The next work investigates developer-environment subjects before choosing new abstractions.

Current investigation block `MSHP-DEV-A` covers:

- VS Code;
- JetBrains Toolbox and IDE ecosystem;
- Lua/LuaJIT multiversion Windows lifecycle;
- Python multiversion Windows lifecycle;
- Node.js multiversion Windows lifecycle;
- a bounded survey of additional runtimes/toolchains;
- LuaRocks, pip, and npm runtime-bound package ecosystems;
- comparative synthesis before implementation taskification.

## Known gaps

- VS Code installation is technically ready for scoped WinGet promotion, but no selected VS Code desired settings/profile/extension inventory or Settings Sync ownership policy exists yet;
- JetBrains Toolbox installation is technically ready as scoped USER WinGet support; no selected Toolbox settings, IDE product/version policy, IDE settings/plugins, or Backup-and-Sync ownership policy exists yet, and the Toolbox CLI remains explicitly work-in-progress;
- Runtime synthesis now establishes a shared model across Lua/Python/Node: exact runtime instances, an intentionally desired installed-version set, separate selected/default state, backend identity, and exact per-instance discovery/uninstall. The backend remains runtime-specific rather than forcing one universal manager;
- this shared runtime model is not implemented yet; current generic installation provenance assumes package-manager/package identities rather than an explicit many-version runtime subject model;
- LuaRocks research confirms runtime-bound package state needs an explicit environment identity: Lua runtime/version + rocks tree + package inventory. LuaRocks tool installation is separate from any tree inventory; native rocks additionally depend on Lua ABI/header/library and compiler/toolchain compatibility;
- pip research reinforces explicit runtime-bound package environments: deterministic mutation must target an exact interpreter/environment, virtual environments are identities rather than generic scope, externally-managed base interpreters must be respected, and declared desired roots must remain distinct from observed/transitive packages;
- no comparative runtime-bound package-environment/inventory model yet; npm still needs investigation before shared package-environment abstractions are chosen;
- native Windows C/C++ toolchain lifecycle is a concrete future gap: current maintainer work already depends on MSVC/Visual Studio Build Tools, and supported MSVC toolsets can coexist side-by-side; exact Visual Studio/Build Tools/Windows SDK ownership still needs a dedicated investigation;
- .NET SDK/runtime, Java/JDK, Rust, and Go are credible future annexation subjects with meaningful multiversion/selection semantics, but current evidence does not justify executable tasks for all of them yet;
- Ruby and PHP remain plausible ecosystem-specific future subjects but are lower priority without a concrete workload; Perl is intentionally cold unless a real dependency appears.

## Deliberate boundaries / deferred work

- Preserve multiversion coexistence as a first-class desired capability where reasonably possible. Represent deliberately desired multiple versions explicitly rather than treating duplicate discovery as ambiguity.
- Keep lifecycle backend-specific behind shared runtime-instance/desired-set/selection concepts: use first-party or ecosystem managers when strong, direct Machine-Soul ownership only when necessary, and do not mandate one cross-runtime manager.
- Investigate first; let evidence decide whether Machine-Soul manages versions directly or delegates to a version manager. Manager identity and manager-switch migration must remain explicit because changing backends can change prefixes, shims, package state, and ownership.
- Do not require assimilation directives for install-only/runtime subjects.
- Do not invent maintainer configuration or package inventories.
- Do not automatically manage project-local dependency environments. Python virtual environments, requirements/lock files, and similar project dependency state remain project-owned unless an environment is explicitly adopted.
- Do not use pip overrides such as `--break-system-packages` as normal reconciliation policy for externally managed Python interpreters; respect external ownership boundaries.
- Do not promote every common language/toolchain into executable work merely because it exists.
- Treat MSVC/Windows native toolchains as the leading additional near-term investigation candidate; keep .NET/JDK/Rust/Go as structured initiative gaps until concrete demand or roadmap synthesis promotes them.
- Keep Ruby/PHP/Perl deferred unless a real workload makes their lifecycle worth owning.
- Coordinate configuration-specific findings with `MSHP-WIN-CONFIG` instead of duplicating desired-state ownership.

## Related executable tasks

`MSHP-DEV-A-010` through `MSHP-DEV-A-120` form the current investigation/synthesis block. Mutable state and dependencies remain authoritative in [`../agent_tasks.md`](../agent_tasks.md).

## Promotion / closure criteria

Promote implementation work only when an investigation identifies a safe bounded capability and any required maintainer-selected desired state is available.

This initiative may remain OPEN while current runtime/editor implementations are complete if future developer-environment subjects remain intentionally desired but deferred.
