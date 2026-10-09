# MSHP-LAB-A-030 — Investigate space-efficient multi-branch Git workspaces

## Description

Research techniques for many independent checkouts of very large repositories with minimal disk waste and safe simultaneous branch writes.

## Requirements

- Compare git worktree with shared object stores, partial/sparse clones, alternates, reference repos, filesystem reflinks, CoW/snapshots and Git LFS; analyze cleanup, locking, worktree safety, CI and platform differences.

## Constraints / non-goals

- Research only; no repository history changes or forced garbage collection of shared objects.

## Acceptance criteria

- An actionable workspace/storage decision matrix describes a safe prototype.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
