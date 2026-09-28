# MSHP-DEV-B-060 — Implement Lua and LuaJIT multiversion backend

## Description

Implement the Windows Lua runtime backend using Machine-Soul-owned exact versioned runtime prefixes and separate selected/default command routing, covering PUC Lua and LuaJIT as distinct runtime flavors.

## Requirements

- Support explicit side-by-side PUC Lua runtime instances for the maintained 5.1–5.5 lines without relying on package install order.
- Treat LuaJIT as a distinct flavor/identity with its own versioning and acquisition/build lifecycle.
- Use exact versioned prefixes and preserve source/acquisition provenance, architecture, executable paths, and checksums/source identity.
- Prefer trusted prebuilt LuaBinaries where they satisfy the requested exact runtime; support a source-build path where required rather than silently substituting a different patch/version.
- For LuaJIT/source builds, consume the native-toolchain prerequisite/discovery capability from DEV-B-025 and report missing prerequisites instead of silently installing toolchains.
- Expose version-qualified commands naturally and implement a Machine-Soul-owned selected/default routing mechanism independent from acquisition order.
- Implement exact uninstall of one runtime prefix without affecting other Lua/LuaJIT instances.
- Add tests for multiple PUC versions plus LuaJIT, selected/default changes, architecture distinction, prefix isolation, and exact removal.

## Constraints / non-goals

- Do not make Scoop package order or ambient PATH the selected-version policy.
- Do not pretend LuaJIT is merely Lua 5.1.
- Do not require a universal cross-runtime manager.
- Do not manage LuaRocks package trees in this task.
- Do not silently compile with an arbitrary compiler when required native prerequisites are missing.

## Acceptance criteria

- Multiple PUC Lua versions and LuaJIT can coexist as exact owned runtime instances.
- Selected/default `lua` routing is explicit and independent from installed-set order.
- Runtime removal is prefix-exact and provenance-safe.
- Acquisition/build differences stay inside the Lua backend rather than leaking into shared runtime core.

## Validation

- Use the completed Lua investigation plus DEV-B-020 findings and DEV-B-025 native-toolchain capability.
- Test simultaneous 5.x versions + LuaJIT and selected-runtime removal/refusal scenarios.
- Run the repository Python validation suite.
