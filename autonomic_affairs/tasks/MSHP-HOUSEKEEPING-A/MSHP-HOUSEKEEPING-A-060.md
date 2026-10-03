# MSHP-HOUSEKEEPING-A-060 — Close and self-archive housekeeping

## Description

Run the final consistency pass, ensure the repository has no residual housekeeping debt from this block, archive HOUSEKEEPING-A itself once terminal, and leave the repository at a clean boundary for the next deliberately selected workstream.

## Requirements

- Re-run the key searches and validation from HOUSEKEEPING-A.
- Verify every non-HOUSEKEEPING pre-existing incomplete block remains frozen, every terminal pre-existing block is archived, retired agent_tasks naming is not live/current, weirdness findings are fixed or durably recorded, the agent-memory audit has no unresolved high-confidence defect, and Dispatch/Active claims/task navigation are coherent.
- Promote durable housekeeping conclusions out of temporary workspace material where appropriate.
- Mark HOUSEKEEPING-A terminal.
- Move the HOUSEKEEPING-A block directory intact into autonomic_affairs/tasks/archive/MSHP-HOUSEKEEPING-A/.
- Remove HOUSEKEEPING-A rows from the active scheduling index after terminal archival.
- Leave Dispatch empty unless the human separately authorizes another executable task.
- Preserve Standardize baseline agent infrastructure across repositories as the next discussed reminder candidate; do not silently promote or execute it as housekeeping.

## Constraints / non-goals

- Do not thaw frozen work.
- Do not begin the cross-repository baseline-standardization reminder.
- Do not delete uncertain findings just to claim a perfectly clean audit.
- Do not rewrite Git history.

## Acceptance criteria

- HOUSEKEEPING-A is itself archived after completion.
- The active task surface contains only genuinely incomplete/frozen blocks.
- Dispatch is empty absent separate human authorization.
- No Active claim remains for HOUSEKEEPING-A.
- The repository is at a documented clean boundary for selecting the next workstream.

## Validation

- Inspect active/archived task trees and tasks.md together.
- Follow fresh-session navigation after HOUSEKEEPING-A has moved.
- Verify archived HOUSEKEEPING-A task IDs remain resolvable.
