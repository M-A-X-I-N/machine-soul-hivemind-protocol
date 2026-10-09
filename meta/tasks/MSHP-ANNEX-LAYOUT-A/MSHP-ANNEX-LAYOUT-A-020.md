# MSHP-ANNEX-LAYOUT-A-020 — Migrate shared annexation internals into a dedicated library directory

## Description

Following the completed layout design, reorganize shared operational modules into its selected internal directory while preserving app-specific folders and minimal necessary entry points.

## Requirements

- Update import boundaries, wrappers, CLI/test entry points, docs, tooling, current self-managed integrations and fresh-clone validation; avoid duplicate runtime implementations.

## Constraints / non-goals

- Requires the layout design and explicit task dispatch. The directory name itself is delegated to the design task; material public import/API breakage may still require maintainer agreement.

## Acceptance criteria

- Annexation root is application-centric and tests prove unchanged behavioral contracts.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
