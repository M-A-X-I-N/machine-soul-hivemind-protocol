# MSHP-ANNEX-LAYOUT-A-010 — Design minimal per-application annexation directory layout

## Description

Inspect the annexation root and specify a reversible layout that leaves application directories and only unavoidable top-level files while moving reusable shared internals into a clearly separated internal library directory.

## Requirements

- Classify modules/packages, wrappers, tests and import consumers; prefer a dot-prefixed directory when practical, but allow an underscore-prefixed directory or another technically justified clearly separated name; evaluate Python import/package constraints and record the proposed tree. The maintainer has delegated this naming choice to the design task.

## Constraints / non-goals

- Do not move code in the planning phase; do not require a dot-prefixed name if it undermines Python importability. Clear separation, not a specific prefix, is mandatory.

## Acceptance criteria

- A technically justified layout plan identifies all affected paths, coupling and rollback requirements; the design task may choose the name without another maintainer naming decision.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
