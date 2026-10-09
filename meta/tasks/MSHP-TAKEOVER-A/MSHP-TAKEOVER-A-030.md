# MSHP-TAKEOVER-A-030 — Implement bounded takeover lifecycle and pilot backends

## Description

Implement the reviewed takeover contract for only identity-verifiable bounded scenarios, prove safety before wider expansion.

## Requirements

- Add plan/verify/mutate/rollback APIs, explicit confirmation, candidate-exact adoption, preservation of unrelated user state, provenance transitions and failed migration recovery; test selected Windows/Linux pilots.

## Constraints / non-goals

- Requires accepted takeover design; broad opaque MSI/EXE migration is not assumed feasible.

## Acceptance criteria

- Pilots safely adopt or migrate explicitly approved installations and reject ambiguous/destructive scenarios.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
