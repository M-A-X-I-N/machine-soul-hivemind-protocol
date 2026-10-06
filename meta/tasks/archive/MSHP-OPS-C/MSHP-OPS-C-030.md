# MSHP-OPS-C-030 — Improve task-ledger block readability

## Description

Make task blocks visually distinct in the authoritative ledger so large numbers of tasks do not blur into one monolithic table.

## Requirements

- Inventory scripts/tests/docs that parse or assume the current monolithic task table.
- Prefer clear per-block headings/tables while preserving Dispatch and task-contract semantics.
- Update affected parsers/tests/navigation if the structure changes.
- Keep incomplete blocks and archival rules understandable.

## Constraints / non-goals

- Do not optimize purely for decoration.
- Do not break machine lookup to improve human appearance.
- Do not rename `agent_tasks` paths in this task.

## Acceptance criteria

- Task blocks are visually obvious.
- Existing task lookup/state tooling still works.
- No scheduling semantics change unintentionally.

## Validation

- Run/search all known ledger consumers and link checks.
