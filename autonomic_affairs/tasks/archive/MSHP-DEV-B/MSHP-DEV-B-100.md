# MSHP-DEV-B-100 — Integrate developer runtime and package lifecycle

## Description

Integrate and validate the first developer-annexation implementation phase end to end: install-only editors, runtime instance sets/backends, runtime-bound package environments, lifecycle dependency ordering, documentation, and initiative status.

## Requirements

- Exercise the VS Code/Toolbox installation declarations through existing application orchestration without introducing config ownership.
- Validate Python, Node, and Lua/LuaJIT simultaneous runtime-instance workflows through the shared runtime core.
- Validate pip/npm/LuaRocks package environments through the shared package-environment core.
- Enforce runtime-removal ordering when owned package environments still reference a runtime.
- Validate selected/default runtime changes independently from package inventory.
- Validate manager/backend mismatch and migration refusal semantics.
- Ensure project-owned environments/config remain outside global annexation.
- Ensure secret redaction/non-persistence boundaries are covered.
- Update architecture/user/agent documentation with the implemented runtime/package-environment model and concrete backend support.
- Update MSHP-DEV-ENV to distinguish implemented capabilities from remaining configuration/plugin/native-toolchain gaps.

## Constraints / non-goals

- Do not invent maintainer-selected VS Code/JetBrains settings, extensions/plugins, IDE versions, or runtime/package inventories.
- Do not close MSHP-DEV-ENV while deliberate future gaps remain.
- Do not add unsupported runtime/package ecosystems just to broaden tests.
- Do not perform manager migrations unless a separately designed migration task exists.

## Acceptance criteria

- Cross-layer tests prove exact runtime/package-environment ownership and safe lifecycle ordering.
- Existing ordinary application installation/configuration behavior remains regression-safe.
- Documentation accurately describes what Machine-Soul can and cannot annex.
- Initiative/task state contains no duplicate ownership with MSHP-WIN-CONFIG.

## Validation

- Run the full repository validation suite available to the agent/CI.
- Inspect GitHub Actions/checks and fix regressions before completion.
- Walk at least: multiple runtimes; default switch; owned package roots; unknown package preservation; blocked runtime removal; project-owned environment; editor install-only declaration.
