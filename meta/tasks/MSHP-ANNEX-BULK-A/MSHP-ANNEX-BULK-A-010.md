# MSHP-ANNEX-BULK-A-010 — Design declarative desired installation sets

## Description

Define a host-aware desired-app/package selection model, separate from configuration precedence, which can be reviewed and applied in bulk without inventing user packages.

## Requirements

- Cover host defaults, optional user overlays, platform constraints, package vs runtime instances, versions, scopes, dependency order, missing packages, config-vs-install separation, skip and resume behavior.

## Constraints / non-goals

- No actual host inventory or defaults are fabricated; research and schema only.

## Acceptance criteria

- A documented minimal schema and planning/safety model can drive both interactive and non-interactive workflows.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
