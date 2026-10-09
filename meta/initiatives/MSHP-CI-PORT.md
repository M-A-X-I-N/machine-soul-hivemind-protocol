# MSHP-CI-PORT — Portable and interoperable CI

**Status:** OPEN

## Goal

Understand whether CI logic can survive a move between GitHub Actions, GitLab CI and independently executable CI systems while retaining MSHP's conservative selector and meaningful validation boundaries.

## Current state / coverage

GitHub Actions centralized selection, reusable Linux/Windows workflows and CodeQL scheduling already exist; no GitLab or portable CI mechanism has been selected.

## Known gaps

- GitLab CI runner/control-plane feature comparison and hosting requirements.
- Portable self-hostable CI workflow engines/languages, especially mixed Windows/Linux execution.
- Interoperability and low-lock-in design with a testable small pilot.

## Deliberate boundaries / deferred work

- Do not replace currently functioning Actions before evidence supports it.
- Separate provider event triggers/secrets/artifacts from portable build/test logic.
- A language or build runner alone is not necessarily a complete CI platform.

## Related executable tasks

- [`MSHP-CI-PORT-A-010`](../tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-010.md)
- [`MSHP-CI-PORT-A-020`](../tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-020.md)
- [`MSHP-CI-PORT-A-030`](../tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-030.md)
- [`MSHP-CI-LAYOUT-A-010`](../tasks/MSHP-CI-LAYOUT-A/MSHP-CI-LAYOUT-A-010.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

Research plus a deliberate platform/interop decision, and either an implemented accepted approach or an explicit deferral outside MSHP's desired support surface.
