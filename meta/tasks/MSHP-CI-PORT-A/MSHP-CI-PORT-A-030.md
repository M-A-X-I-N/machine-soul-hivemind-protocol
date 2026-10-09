# MSHP-CI-PORT-A-030 — Design CI interoperability options

## Description

Synthesize the GitLab and portable CI research into concrete options for sharing check logic among GitHub Actions, GitLab and local/self-hosted runners.

## Requirements

- Analyze reusable scripts versus common execution engine versus translated workflow definitions; map event/selector/CodeQL/secrets/artifacts responsibilities, degraded modes and backward compatibility; identify a smallest migration slice.

## Constraints / non-goals

- Do not replatform or duplicate authoritative CI selectors as part of this task.

## Acceptance criteria

- An interoperability design recommends a bounded follow-up pilot or documents why no interchange is worthwhile.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
