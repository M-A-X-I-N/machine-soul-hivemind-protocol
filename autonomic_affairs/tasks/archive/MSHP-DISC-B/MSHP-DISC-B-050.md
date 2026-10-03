# MSHP-DISC-B-050 — Implement Windows POSIX installation discovery

## Description

Implement installation discovery for Bash, Zsh, and Fish in the Windows POSIX compatibility environment that Machine-Soul actually targets for their configuration, rather than confusing native Windows PATH/package state with the configured runtime.

## Requirements

- Discover and describe the active compatibility environment used by WindowsPosixHomeDestination sufficiently to scope shell discovery.
- Support the package/executable evidence mechanisms actually used by the supported MSYS2/Cygwin-style environments, validating their native package-query interfaces before parsing them.
- Discover Bash, Zsh, and Fish executable paths/versions and package registration within that target environment.
- Preserve compatibility-environment identity in observations/candidates so two installed environments are not silently treated as one installation.
- If multiple environments/candidates are visible, retain them and report ambiguity/selection facts honestly.
- Wire Windows declarations for Bash, Zsh, and Fish to the new discovery plans and enable CHECK_INSTALLED where meaningful.
- Reuse the shared installation assessment model and generic executable observations from MSHP-DISC-B-020.
- Keep destination-resolution and installation-discovery environment assumptions aligned.
- Use ../MSHP-DISC-A/workspace/installation_discovery.md as the investigation basis.

## Constraints / non-goals

- Do not scan arbitrary native Windows executables and call them the configured POSIX shell.
- Do not install or modify MSYS2/Cygwin packages.
- Do not require every possible POSIX compatibility layer.
- Do not implement shell configuration verification; that is MSHP-DISC-B-070.

## Acceptance criteria

- Windows shell installation state is reported for the environment Machine-Soul configures.
- Package registration, executable/version, environment identity, and Machine-Soul ownership remain separate observations.
- Missing/unavailable compatibility-environment tooling produces honest unknown/unsupported results rather than false absence.
- Current Windows shell configuration behavior remains unchanged.

## Validation

- Unit-test environment identity, package/executable candidates, backend unavailable, and multi-environment ambiguity.
- Extend Windows POSIX integration tests using controlled/fake discovery backends where hosted CI lacks all real package managers.
- Run full CI.
