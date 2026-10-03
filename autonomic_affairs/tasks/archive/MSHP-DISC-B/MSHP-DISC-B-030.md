# MSHP-DISC-B-030 — Implement Linux installation discovery

## Description

Implement granular installation discovery for the current Linux application set using authoritative native package data plus executable/version evidence, while preserving alternate/manual candidates and uncertainty.

## Requirements

- Implement exact dpkg package-registration discovery with installed status, package identity, version, architecture/source fields when useful, and package-file ownership where available.
- Implement executable/path/version observations through the generic discovery framework.
- Add Flatpak discovery only for current applications whose verified upstream identity/use justifies it; verify exact IDs before declaring them.
- Wire current Linux declarations for Bash, Zsh, Fish, Oh My Posh, and Contour to meaningful discovery plans.
- For Fish, distinguish exact dpkg package compatibility with the preferred AptPackage strategy from historical apt acquisition, which may remain unknown.
- For Oh My Posh, preserve user-scoped/manual executable candidates such as upstream-script layouts rather than requiring native package registration.
- For Contour, retain multiple legitimate package/manual candidates instead of forcing one mechanism.
- Mark CHECK_INSTALLED supported on Linux where the declared plan can produce a meaningful assessment even if Install/Uninstall remain unimplemented.
- Define absence only after all declared authoritative probes that are available complete without candidates; backend failures/permission/tool absence must yield unknown where appropriate.
- Preserve candidate scope, paths, versions, registration identity, preferred match, ownership, and evidence in machine-readable results.
- Use ../MSHP-DISC-A/workspace/installation_discovery.md as the investigation source.

## Constraints / non-goals

- Do not claim dpkg registration proves apt historically installed the package.
- Do not implement every Linux distribution/package manager.
- Do not mutate packages, PATH, or application state during discovery.
- Do not implement takeover.

## Acceptance criteria

- Current Linux applications can report richer installed/absent/unknown/ambiguous state independently from install capability.
- Preferred package matches, foreign/manual candidates, and Machine-Soul ownership are distinguishable.
- Multiple candidates survive aggregation.
- Existing Linux Install/Uninstall behavior remains safe.

## Validation

- Unit-test dpkg present/absent/error, executable-only foreign candidates, candidate merging, and stale Machine-Soul provenance.
- Exercise representative Fish, OMP, Bash/Zsh, and Contour declarations.
- Run Linux application/install/matrix tests and full CI.
