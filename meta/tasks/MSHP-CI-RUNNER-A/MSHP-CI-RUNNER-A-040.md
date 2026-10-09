# MSHP-CI-RUNNER-A-040 — Investigate self-hosted-first hosted-runner fallback

## Description

Research whether GitHub Actions can dynamically use an idle self-hosted VM runner and automatically fall back to GitHub-hosted runners when capacity is unavailable.

## Requirements

- Study labels, registration/state APIs, queue timeouts, reusable workflow indirection, trusted status/availability probes, dispatch and failures; distinguish scheduling before queueing from mid-job migration.

## Constraints / non-goals

- Research only; don't break normal GitHub-hosted CI or produce a deadlock when home infrastructure is down.

## Acceptance criteria

- A fail-safe routing design clearly defines selection, timeout, fallback and security consequences.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
