# MSHP-HOUSEKEEPING-A-010 — Establish housekeeping freeze boundary

## Description

Make HOUSEKEEPING-A the only executable workstream while repository cleanup is underway, and record an authoritative inventory of what is frozen, terminal, active, remembered, and eligible for later cleanup.

## Requirements

- Treat all pre-existing task blocks as outside the active housekeeping workstream.
- Preserve terminal task states (COMPLETE, CANCELLED, SUPERSEDED) as terminal rather than rewriting them to FROZEN.
- Ensure every pre-existing non-terminal task outside HOUSEKEEPING-A is FROZEN.
- Ensure Dispatch contains only the currently authorized HOUSEKEEPING-A task.
- Ensure no unrelated Active claim survives.
- Inventory every current task block and lifecycle state, every archival candidate, every frozen/incomplete block, current reminders, current initiatives, the .agents memory/instruction tree, and relevant governance documentation.
- Persist the inventory in the HOUSEKEEPING-A workspace.

## Constraints / non-goals

- Do not archive blocks yet.
- Do not rewrite completed tasks to FROZEN.
- Do not thaw any pre-existing frozen work.
- Do not perform memory/document cleanup beyond corrections strictly required to establish the boundary.
- Do not promote reminders or initiatives.

## Acceptance criteria

- HOUSEKEEPING-A is the only executable task block.
- Every other incomplete pre-existing task is frozen.
- Terminal blocks remain terminal.
- Dispatch and Active claims are consistent.
- A durable inventory exists for the remaining housekeeping tasks.

## Validation

- Re-read autonomic_affairs/tasks.md and verify no pre-existing task outside HOUSEKEEPING-A is QUEUED, IN_PROGRESS, BLOCKED, or AWAITING_DEFERRED_CI.
- Verify the inventory matches the live repository tree and lifecycle metadata.
