# MSHP-CI-PORT-A-020 — Investigate portable or self-hostable CI workflow systems

## Description

Survey genuinely portable CI definitions or engines (for example Dagger, Earthly, Taskfile and similar systems), checking which are languages, local execution engines, CI orchestration services, or merely configuration generators.

## Requirements

- Compare portability, Windows/Linux support, containers and virtualization, cache/state handling, secrets, parallel jobs, self-hosted execution, observability and provider lock-in; test representative workflows only when safe.

## Constraints / non-goals

- Do not assume any advertised portability includes Windows guests, privileged workloads or equivalent hosted services.

## Acceptance criteria

- A ranked decision matrix gives technically plausible portable CI candidates and limitations.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
