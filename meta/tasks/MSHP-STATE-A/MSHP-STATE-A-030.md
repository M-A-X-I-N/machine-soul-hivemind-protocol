# MSHP-STATE-A-030 — Migrate annexation ownership records and durable action logs

## Description

Move eligible claimed install/deployment state and meaningful annexation event logs from scratch to the versioned application data layer.

## Requirements

- Document state classification and retention, one-time migration, rollback, legacy-read safety, log sensitivity and noisy ephemeral data left in scratch; preserve exact application ownership provenance.

## Constraints / non-goals

- Depends on versioned storage API; no insecure broad logging of secrets.

## Acceptance criteria

- Previously managed state remains recoverable with validated migrations and clear scratch separation.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
