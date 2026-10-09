# MSHP-WINGET-A-020 — Investigate custom and non-default WinGet sources

## Description

Investigate non-default/custom WinGet source semantics as a trust, identity, provenance, and lifecycle problem after the Store investigation establishes the source model.

## Requirements

- Map source add/remove/update/reset/export/import behavior and machine-readable source identity.
- Investigate trust/signature/authentication implications, private/custom manifests, duplicate package IDs across sources, and deterministic package selection.
- Determine whether source identity must be persisted as part of package ownership/provenance and how source lifecycle interacts with owned packages.
- Distinguish source management from package management where appropriate.

## Constraints / non-goals

- Do not implement source management here.
- Do not treat custom sources as trusted merely because WinGet accepts them.

## Acceptance criteria

- A durable source/provenance model exists.
- Identity-collision and removal/restoration semantics are explicit.
- Any implementation tasks are evidence-backed.

## Validation

- Use current official WinGet/Microsoft documentation plus safe experiments where needed.
