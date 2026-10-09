# MSHP-TAKEOVER-A-020 — Specify takeover planning, consent and rollback contracts

## Description

Design an explicit dry-run-first takeover operation separating proof of identity, desired backend, affected state, required backups and human approval.

## Requirements

- Include exact provenance transitions, partial failure recovery, destination conflicts, instance/version/scope mismatches, audit trail and conservative cross-account behavior; define an explicit maintainer gate for destructive migrations.

## Constraints / non-goals

- Depends on research; no silent installation ownership changes or bypass of package manager constraints.

## Acceptance criteria

- A reviewed design and test matrix make implementation boundaries clear.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
