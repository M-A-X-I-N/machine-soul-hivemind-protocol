# MSHP-ANNEX-UPDATE-A-020 — Implement a shared update operation with backend pilots

## Description

After update semantics are agreed, build an explicit update operation through the generic annexation engine and a small representative owned-package backend set.

## Requirements

- Provide capability declarations, scoped provenance, explicit user intent, bounded rollback/reporting, non-mutating discovery and targeted Windows/Linux tests; do not infer backend support from presence.

## Constraints / non-goals

- Requires completion of update design and any material maintainer decision; no code in current planning pass.

## Acceptance criteria

- Owned applications can be checked and updated safely through one composable operation, and unsupported backends refuse visibly.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
