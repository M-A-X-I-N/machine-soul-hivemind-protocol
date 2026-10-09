# MSHP-ANNEX-BULK-A-040 — Validate fresh-host bulk bootstrap flows

## Description

Exercise planned multi-app install and per-host package profiles across supported fresh-machine scenarios.

## Requirements

- Verify idempotent retries, dependency ordering, offline/unavailable backends, installation-scope exactness, partial success, user cancellation and no fabricated install ownership.

## Constraints / non-goals

- Depends on bulk list/profile capabilities; use disposable or controlled environments.

## Acceptance criteria

- Repeatable validation proves single-session bootstrap without losing atomic safety guarantees.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
