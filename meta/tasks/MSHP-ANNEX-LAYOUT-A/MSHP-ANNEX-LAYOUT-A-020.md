# MSHP-ANNEX-LAYOUT-A-020 — Migrate shared annexation internals into a hidden directory

## Description

After layout approval, reorganize shared operational modules into the selected internal directory while preserving app-specific folders and minimal necessary entry points.

## Requirements

- Update import boundaries, wrappers, CLI/test entry points, docs, tooling, current self-managed integrations and fresh-clone validation; avoid duplicate runtime implementations.

## Constraints / non-goals

- Requires design and maintainer agreement on any externally visible import breaking changes.

## Acceptance criteria

- Annexation root is application-centric and tests prove unchanged behavioral contracts.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
