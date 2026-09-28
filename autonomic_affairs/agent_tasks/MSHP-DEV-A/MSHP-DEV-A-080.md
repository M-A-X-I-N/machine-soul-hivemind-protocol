# MSHP-DEV-A-080 — Investigate LuaRocks annexation

## Description

Investigate LuaRocks as a package ecosystem whose semantics depend on Lua runtime/version identity and package-tree selection.

## Requirements

- Research current Windows LuaRocks installation and supported Lua-version binding.
- Map local/system/user trees, Lua version selection, Lua directory selection, configuration files, and per-version package trees.
- Investigate coexistence of multiple Lua versions and multiple LuaRocks trees.
- Investigate deterministic package list/install/uninstall/export interfaces.
- Identify scope/tree identity required for safe ownership.
- Separate LuaRocks tool installation from packages it manages.
- Assess whether Machine-Soul should initially manage only LuaRocks installation, selected package inventories, or both.
- Identify native-build/toolchain dependencies and machine-specific concerns.

## Constraints / non-goals

- Do not install LuaRocks or rocks.
- Do not assume one global package tree.
- Do not design generic package-manager machinery before comparative synthesis.
- Do not require config assimilation if package-manager installation/inventory is the only useful capability.

## Acceptance criteria

- LuaRocks-to-Lua-version/tree binding is explicit.
- Safe ownership/inventory boundaries are mapped.
- Findings can be compared meaningfully with pip and npm.

## Validation

- Use current LuaRocks documentation/upstream.
- Walk at least two simultaneous Lua versions with distinct package trees.
