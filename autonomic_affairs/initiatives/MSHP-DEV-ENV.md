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
- Lua research found no single clean native-Windows manager for PUC Lua 5.1–5.5 + LuaJIT; versioned runtime instances plus separately managed default selection is the leading model, while the acquisition backend remains open pending Python/Node comparison; no chosen Python/Node backend yet;
- no generic representation yet for intentionally desired simultaneous runtime versions;
- no runtime-bound package-environment/inventory model yet;
- many possible future runtimes/toolchains/package managers remain intentionally uninvestigated.

## Deliberate boundaries / deferred work

- Preserve multiversion coexistence as a desirable capability where reasonably possible, but do not build custom version-management machinery when a sane maintained ecosystem solution is better.
- Investigate first; let evidence decide whether Machine-Soul manages versions directly or delegates to a version manager.
- Do not require assimilation directives for install-only/runtime subjects.
- Do not invent maintainer configuration or package inventories.
- Do not automatically manage project-local dependency environments.
- Do not promote every common language/toolchain into executable work merely because it exists.
- Coordinate configuration-specific findings with `MSHP-WIN-CONFIG` instead of duplicating desired-state ownership.

## Related executable tasks

`MSHP-DEV-A-010` through `MSHP-DEV-A-120` form the current investigation/synthesis block. Mutable state and dependencies remain authoritative in [`../agent_tasks.md`](../agent_tasks.md).

## Promotion / closure criteria

Promote implementation work only when an investigation identifies a safe bounded capability and any required maintainer-selected desired state is available.

This initiative may remain OPEN while current runtime/editor implementations are complete if future developer-environment subjects remain intentionally desired but deferred.
