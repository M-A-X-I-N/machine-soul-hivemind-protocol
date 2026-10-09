# MSHP-PKG-RESEARCH-A-030 — Research pipx and user-local application package managers

## Description

Investigate pipx and representative user-local app installers as distinct from project-local pip environments and generic application package managers.

## Requirements

- Review executable shims, per-user locations, Python runtime coupling, metadata discovery, upgrade/reinstall, ownership, scopes and removal guards.

## Constraints / non-goals

- Research only; don't silently adopt existing pipx venvs.

## Acceptance criteria

- A candidate backend/ownership plan is documented with overlap to existing Python package-environment machinery.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
