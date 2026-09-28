# MSHP-DEV-A-030 — Investigate Lua multiversion annexation

## Description

Investigate sane Windows Lua annexation while preserving the option to run multiple Lua versions simultaneously. Lua is an adversarial multiversion case, not a pretext to invent bespoke architecture.

## Requirements

- Research current Windows installation options for Lua 5.1, 5.2, 5.3, 5.4 and LuaJIT where relevant.
- Identify maintained/reputable version managers, package managers, prebuilt distributions, and native side-by-side approaches.
- Map executable naming/path collisions and deterministic version selection.
- Investigate architecture variants, installation scope, and install locations relevant to coexistence.
- Investigate discovery/version probing for every installed runtime.
- Investigate uninstall semantics that remove one version without damaging others.
- Identify how LuaRocks binds to Lua versions, leaving detailed package-manager work to DEV-A-080.
- Compare delegation to an existing version manager with Machine-Soul-managed side-by-side installations.
- Determine what desired state would need to represent: version set, selected/default version, backend/manager, executable identity, architecture, and aliases/shims.
- Treat multiversion coexistence as desirable when reasonably possible, without requiring custom Machine-Soul machinery if the ecosystem already solves it better.

## Constraints / non-goals

- Do not install/uninstall Lua.
- Do not preselect a version manager.
- Do not invent a generic runtime abstraction during this investigation.
- Do not implement LuaRocks package inventories here.
- Do not create assimilation directives merely to make Lua look complete.

## Acceptance criteria

- A sane current Windows multiversion approach is identified, or the absence of one is demonstrated.
- Tradeoffs between direct side-by-side management and version-manager delegation are explicit.
- Discovery/install/uninstall/default-selection semantics are understood.
- Findings are comparable with Python and Node.

## Validation

- Prefer current authoritative/upstream sources.
- Validate coexistence claims for all relevant maintained Lua versions.
- Call out abandoned/stale version-manager advice explicitly.
