# MSHP-HOUSEKEEPING-A-020 — Archive all terminal task blocks

## Description

Move every dead/done task block out of the active task surface and into the structured task archive, then change the task-storage contract so terminal blocks are archived rather than retaining a rolling pair of completed blocks in the active index.

## Requirements

- Use the inventory from MSHP-HOUSEKEEPING-A-010.
- Treat a block as archival-eligible only when every task in that block is terminal: COMPLETE, CANCELLED, or SUPERSEDED.
- Move every eligible active block directory intact under autonomic_affairs/tasks/archive/<block-id>/, preserving task specs and workspaces.
- Remove archived block rows from the active autonomic_affairs/tasks.md index.
- Preserve incomplete/frozen blocks in the active task tree.
- Replace the current retain-two-recent-completed-blocks rule with a terminal-block archival rule across task/storage/recovery documentation.
- Preserve immutable task IDs and valid lookup/navigation after moves.
- Do not archive HOUSEKEEPING-A while it is still active; its own archival belongs to the final housekeeping task.

## Constraints / non-goals

- Do not delete historical task/workspace material merely because it is old.
- Do not rewrite task IDs.
- Do not thaw or modify the intent of frozen blocks.
- Do not collapse archived blocks into a monolithic document.
- Do not alter legacy V2 storage except where navigation wording must remain consistent.

## Acceptance criteria

- Every pre-HOUSEKEEPING terminal block lives under tasks/archive/.
- No terminal pre-HOUSEKEEPING block remains in the active task tree or active task index.
- Every incomplete/frozen block remains active.
- Task lookup/documentation reflects archive-all-terminal-blocks policy.
- Internal links/navigation remain valid.

## Validation

- Compare active task directories, archive directories, and task-index rows.
- Search authoritative task documentation for the obsolete two-recent-completed-blocks retention rule.
- Check archived task links and IDs remain resolvable.
