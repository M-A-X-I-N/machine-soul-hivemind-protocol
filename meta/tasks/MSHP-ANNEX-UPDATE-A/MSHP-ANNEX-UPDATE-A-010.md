# MSHP-ANNEX-UPDATE-A-010 — Design safe application update semantics

## Description

Investigate update detection, version intents, pinned channels, ownership, package-manager behavior, rollback expectations and concurrent updates for MSHP-managed applications.

## Requirements

- Cover WinGet, Apt, externally managed/manual installations, runtime-instance sets and package environments without confusing updates with install/selection; define Check, Plan/dry-run and Update contracts.

## Constraints / non-goals

- Do not trigger updates during discovery, Check, Apply or routine status; don't claim unmanaged applications.

## Acceptance criteria

- A documented update model and backend rollout plan handle managed versus unmanaged and multi-version boundaries.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
