# MSHP-DEV-A-050 — Investigate Node multiversion annexation

## Description

Investigate Node.js on Windows as a multiversion runtime/engine annexation subject, including the current version-manager ecosystem and its interaction with npm and Corepack.

## Requirements

- Research current official Node Windows installation and supported side-by-side/version-manager approaches.
- Compare maintained Windows-capable managers such as fnm, nvm-windows, Volta, mise, or other current credible options without assuming one is preferred.
- Map version storage, current/default selection, shims/PATH behavior, discovery, update, and uninstall.
- Investigate discovery of installed versions independently from whichever manager is active.
- Separate Node versions from npm global packages and Corepack-managed package-manager shims.
- Investigate how npm/Corepack state binds to Node versions and what changes when switching versions.
- Compare delegation to a selected version manager with direct runtime management.
- Produce conceptual outputs comparable with Lua and Python.

## Constraints / non-goals

- Do not install/uninstall Node or version managers.
- Do not manage npm package inventories here.
- Do not assume one version manager is universally best.
- Do not force Node into a language-specific architecture if generic annexation machinery suffices.

## Acceptance criteria

- Current Windows multiversion Node options and tradeoffs are mapped.
- Version/default-selection/discovery/uninstall semantics are explicit.
- npm/Corepack boundaries are understood without prematurely solving package inventories.
- Findings are comparable with Lua and Python.

## Validation

- Use current Node and version-manager documentation.
- Verify maintenance and current Windows support for compared managers.
- Record manager-specific storage/shim quirks relevant to ownership/discovery.
