# MSHP-ANNEX-BULK-A-020 — Add multi-select installation workflow

## Description

Plan implementation of one interactive list of available installable application/package targets with bulk selection, previews and confirmed execution instead of one app-at-a-time menus.

## Requirements

- Reuse atomic wrappers and shared orchestration; allow toggling selections, explain unsupported/uninstalled/unmanaged states, plan/cancel, continue-on-failure policy and clear per-operation results.

## Constraints / non-goals

- Requires design; does not bypass install ownership, confirmation, dependencies or safe partial-failure rules.

## Acceptance criteria

- One interaction can select many targets and invoke their existing install operations safely.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
