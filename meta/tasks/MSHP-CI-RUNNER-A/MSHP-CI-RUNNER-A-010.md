# MSHP-CI-RUNNER-A-010 — Design nested-virtualized self-hosted CI control plane

## Description

Investigate placing a generic GitHub Actions self-hosted runner/controller inside an Ubuntu workhorse VM while running isolated Linux/Windows CI guest workloads via nested virtualization.

## Requirements

- Check actual hypervisor capabilities, licensing and availability of official runner images, runner/job boundaries, sandbox isolation, rollback, permissions, worker registration and future non-GitHub CI adapters.

## Constraints / non-goals

- Research only; do not assume GitHub-hosted runner images can be reproduced locally byte-for-byte.

## Acceptance criteria

- A viable topology and explicit hardware/OS constraints are documented.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
