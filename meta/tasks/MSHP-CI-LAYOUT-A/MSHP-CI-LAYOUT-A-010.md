# MSHP-CI-LAYOUT-A-010 — Relocate exclusively CI-owned scripts into .github

## Description

Plan and execute later a focused layout migration placing scripts used only by GitHub CI beneath .github, including the selector and its exclusive helpers, without changing their semantics.

## Requirements

- Inventory all call sites, workflows, CI-specific tests and docs; classify genuinely shared scripts separately; move CI-only files under a clear .github subdirectory; update imports, runner steps and check selection paths; retain reusable repository logic outside when truly cross-purpose.

## Constraints / non-goals

- This planning entry does not move files; the future task must not change CI behavior or destroy coverage.

## Acceptance criteria

- All CI-exclusive scripts have a defined .github home and equivalent selector/workflow/tests pass after relocation.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
