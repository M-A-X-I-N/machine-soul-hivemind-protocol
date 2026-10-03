# MSHP-DEV-A-100 — Investigate npm annexation

## Description

Investigate npm as a Node-bound package manager, including global package scope/prefix behavior and interactions with Node version managers.

## Requirements

- Map npm installation/bundling with Node and how npm versions vary across Node/runtime-manager choices.
- Investigate global package prefix/root behavior on Windows and how version managers affect it.
- Investigate package inventory/install/uninstall interfaces and whether global inventories survive/switch with Node versions.
- Separate npm itself from packages it manages.
- Investigate Corepack and alternative package-manager shims only where they materially affect npm/Node ownership boundaries.
- Assess whether Machine-Soul should manage global package inventories, selected project environments, or only npm/runtime installation initially.
- Identify registry authentication/tokens and other secret state that must remain outside tracked desired state.
- Map deterministic ownership when multiple Node versions/managers coexist.

## Constraints / non-goals

- Do not install npm packages.
- Do not store registry credentials/tokens.
- Do not automatically manage project-local dependencies.
- Do not design shared package-manager machinery before synthesis.

## Acceptance criteria

- Node/npm/version-manager ownership relationships are explicit.
- Global package/prefix behavior under multiversion Node is understood.
- Safe package-inventory boundaries are identified.
- Findings are comparable with LuaRocks and pip.

## Validation

- Use current npm/Node/version-manager documentation.
- Walk direct Node, version-managed Node, global package, and manager-switch scenarios.
