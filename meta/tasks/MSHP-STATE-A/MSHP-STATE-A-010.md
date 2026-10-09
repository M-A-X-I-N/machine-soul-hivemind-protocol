# MSHP-STATE-A-010 — Design durable per-user application-state storage

## Description

Specify MSHP-owned persistent state on Windows and Linux, with migration/versioning and security/lifecycle separation from disposable scratch.

## Requirements

- Compare LOCALAPPDATA versus APPDATA, XDG_STATE_HOME or equivalent, host/account scope, sensitive logs, ownership provenance, backup/disaster recovery, schema IDs, migrations and portability.

## Constraints / non-goals

- No state move or schema choice until design accepted; secrets remain protected and machine-local.

## Acceptance criteria

- A versioned storage architecture clearly separates long-lived operational state from scratch.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
