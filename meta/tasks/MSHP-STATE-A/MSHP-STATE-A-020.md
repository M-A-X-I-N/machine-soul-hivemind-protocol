# MSHP-STATE-A-020 — Implement versioned cross-platform state location and migrations

## Description

Build a shared storage API for durable machine/account-scoped state after the storage design settles.

## Requirements

- Include safe directory creation, permissions, schema version detection, forward migrations, incompatible-version refusal, transactional backups/recovery and testable platform path overrides.

## Constraints / non-goals

- Do not make current operation records disappear or silently merge distinct account/host histories.

## Acceptance criteria

- A verified storage API initializes, reads and safely migrates state on Windows and Linux.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
