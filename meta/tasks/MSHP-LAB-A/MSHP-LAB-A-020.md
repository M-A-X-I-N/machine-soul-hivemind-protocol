# MSHP-LAB-A-020 — Design shared workhorse scheduling for multiple agents

## Description

Plan safe concurrent agent access to one workhorse without proliferating full VMs.

## Requirements

- Compare leases/queues, isolated users, containers, disposable worktrees, task concurrency, port/resource limits, credential isolation, cleanup, stale-lease recovery and ownership attribution.

## Constraints / non-goals

- Depends on remote-control research; do not promise isolation without verifying threat boundaries.

## Acceptance criteria

- A capacity-aware orchestration design supports independent tasks and protects concurrent agents.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
