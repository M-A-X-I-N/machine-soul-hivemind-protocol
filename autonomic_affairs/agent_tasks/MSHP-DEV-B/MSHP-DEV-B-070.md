# MSHP-DEV-B-070 — Implement package-environment annexation core

## Description

Implement the shared package-environment/inventory model justified by LuaRocks, pip, and npm while preserving manager-specific environment identity and commands.

## Requirements

- Add typed package-environment identity with manager/backend identity, optional exact runtime-instance reference, backend-specific environment locator, environment classification, ownership/adoption state, and mutation policy.
- Represent declared desired root packages separately from observed roots and transitive dependency closure.
- Preserve manager-native desired package specifiers while allowing normalized package identity for comparison/presentation.
- Support conservative ownership states including Machine-Soul-created, explicitly adopted, externally-managed/read-only, project-owned, and ephemeral/unmanaged.
- Add backend protocol/strategy hooks for environment discovery, inventory discovery, install/update/remove, and verification.
- Keep package-manager tool availability/lifecycle separate from environment lifecycle and package inventory.
- Preserve unknown/unowned top-level packages by default; removing a package requires Machine-Soul root ownership or an explicitly stronger environment policy.
- Prevent runtime removal/migration from orphaning owned package environments through explicit dependency checks/hooks.
- Add secret-safe diagnostic/result contracts so backend output cannot accidentally persist registry credentials.
- Add unit/state/provenance tests for environment identity, desired roots, unmanaged packages, read-only environments, and runtime dependency ordering.

## Constraints / non-goals

- Do not implement LuaRocks, pip, or npm commands in the shared core.
- Do not define one universal GLOBAL/USER filesystem scope that erases backend semantics.
- Do not auto-own project environments or lockfiles.
- Do not add exclusive deletion semantics as the default for adopted environments.
- Do not store registry/index credentials.

## Acceptance criteria

- Multiple environments for the same runtime/manager can coexist with exact identity.
- Desired roots and observed/transitive packages remain distinct in state and reconciliation.
- Read-only/project/ephemeral environments cannot be mutated accidentally.
- Runtime lifecycle can detect and refuse unsafe deletion of bound owned environments.

## Validation

- Add cross-backend fake strategies proving the model works with tree-, interpreter-, and prefix-like locators.
- Exercise adoption, unknown packages, read-only refusal, and runtime-removal dependency scenarios.
- Run the repository Python validation suite.
