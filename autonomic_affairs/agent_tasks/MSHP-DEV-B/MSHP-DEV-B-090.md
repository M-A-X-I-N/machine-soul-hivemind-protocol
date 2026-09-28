# MSHP-DEV-B-090 — Implement LuaRocks package backend

## Description

Implement LuaRocks as a runtime-bound package-environment backend using exact Lua runtime + rocks-tree identity and declared desired root inventories.

## Requirements

- Manage/discover the LuaRocks tool separately from any rocks tree inventory.
- Bind each managed package environment to an exact owned Lua/LuaJIT runtime instance plus exact rocks-tree root.
- Invoke LuaRocks with explicit runtime/version/directory and tree selectors rather than ambient PATH/config.
- Support distinct trees for simultaneous Lua versions as the initial safe baseline.
- Discover installed packages with script-oriented output and reconcile declared desired roots through LuaRocks-native install/remove.
- Preserve transitive rocks as observed dependency state rather than independent desired roots.
- Keep project-local trees project-owned unless explicitly adopted.
- Report compiler/Lua-header/external-library prerequisites for native rocks without silently annexing them.
- Add tests for two simultaneous Lua runtime/tree pairs, native-prerequisite failure, unknown packages, and exact tree isolation.

## Constraints / non-goals

- Do not make one global LuaRocks inventory.
- Do not share one physical tree across Lua versions in the initial implementation.
- Do not assimilate the entire LuaRocks config surface merely to manage packages.
- Do not silently select or install native compilers.
- Do not claim arbitrary project trees.

## Acceptance criteria

- Package mutations are exact to one runtime-bound tree.
- Packages in one Lua version/tree cannot be mistaken for another's inventory.
- Desired roots/transitives/unknown roots follow shared package-environment ownership rules.
- Native-build prerequisite failures are explicit and safe.

## Validation

- Re-check current LuaRocks command semantics during implementation.
- Exercise two Lua versions with overlapping package names in distinct fake trees.
- Run the repository Python validation suite.
