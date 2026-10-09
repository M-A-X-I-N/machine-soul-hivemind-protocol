# MSHP-CI-PORT-A-010 — Investigate GitLab CI for Machine-Soul

## Description

Research GitLab CI, its runner model, configuration language, security permissions, self-hosting options and migration costs relative to the existing GitHub Actions selector.

## Requirements

- Map current MSHP checks, matrices, artifacts, schedules, caches, CodeQL/deferred analysis and manual overrides onto GitLab capabilities; distinguish GitLab.com from self-managed GitLab; document constraints and maintenance cost.

## Constraints / non-goals

- Do not migrate CI or modify current workflows during research.

## Acceptance criteria

- A feature-by-feature compatibility and gaps report proposes what, if anything, is worth adopting.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
