# MSHP-DEV-A-090 — Investigate pip annexation

## Description

Investigate pip as an interpreter-bound package manager with explicit separation among global, user, virtual-environment, and externally managed environments.

## Requirements

- Map pip's binding to a specific Python interpreter and deterministic invocation semantics such as `python -m pip`.
- Investigate system/global, user, virtual-environment, and externally-managed-environment constraints.
- Investigate package inventory/export/install/uninstall interfaces and limits of requirements/freeze as desired-state representations.
- Separate pip tool installation from packages pip manages.
- Investigate interaction with multiple simultaneous Python versions.
- Treat virtual environments as environment identities rather than merely package scope.
- Assess which environment inventories, if any, Machine-Soul should manage by default.
- Identify native build, index/authentication, secret, and machine-specific concerns.

## Constraints / non-goals

- Do not install packages.
- Do not automatically claim every virtual environment.
- Do not store index credentials/tokens.
- Do not design shared package-manager machinery before comparative synthesis.

## Acceptance criteria

- Interpreter/environment/package ownership relationships are explicit.
- Safe and unsafe declarative inventory boundaries are identified.
- Findings are comparable with LuaRocks and npm.

## Validation

- Use current Python Packaging/pip documentation.
- Walk system, user, venv, multiple-interpreter, and externally-managed cases.
