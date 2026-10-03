# MSHP-HOUSEKEEPING-A — Repository consistency audit

Recorded for MSHP-HOUSEKEEPING-A-040.

## Mechanical checks

- Parsed all 94 current non-archived Markdown files for relative Markdown link targets against the live Git tree.
- Broken relative link targets found: 0.
- Archived task blocks were moved blob-for-blob; obvious parent-climbing links were checked before archival and no active-task-parent dependency was found.

## High-confidence fixes applied

- Updated reminders.md from retired agent_tasks terminology to current tasks terminology.
- Repaired the legacy V2 archive's current-navigation link from agent_tasks.md to tasks.md.
- Changed task archival policy from rolling recent completed blocks to archive-all-terminal-blocks.
- Archived all pre-housekeeping terminal blocks while preserving task IDs and workspaces.
- Updated live .agents research/memory pointers from moved active task workspaces to their archived paths, including older DISC-A/INST-A material.
- Corrected stale root README wording that said experimental/v2 was still being promoted into main.
- Corrected live investigation wording that said DISC-A workspace material remained temporary/unarchived after that block had already archived.

## Current-authority verification

Direct reads of current files confirm:

- root README no longer says v2 is being promoted now;
- reminders.md no longer points to agent_tasks;
- tasks.md no longer retains a two-completed-block context policy;
- tasks/README.md no longer describes recent completed-block retention;
- .agents/WORKFLOW.md explicitly defines terminal-block archival;
- sampled .agents detailed-research pointers resolve under tasks/archive/.

GitHub code-search results lagged behind several just-written commits during the audit. Direct file/tree reads were treated as authoritative rather than stale search snippets.

## Historical material intentionally retained

- Archived META/OPS-C task specifications continue to mention agent_tasks where the retired name is part of the historical task/migration record.
- Historical CI task specs retain their original policy language where they document an earlier control-plane state.
- Historical experimental/v1/v2 decision notes retain branch names and old snapshot facts when the point of the note is historical evidence.

## Cautious candidates for the deeper agent-memory audit

The following are not declared defects here; A-050 should review them for context burden/staleness while erring toward retention:

- .agents/decisions/v2_stable_baseline.md — useful historical checkpoint, but contains snapshot facts that could be mistaken for current state without context.
- .agents/decisions/main_active_iteration.md — likely still useful, but overlaps root README/WORKFLOW branch doctrine.
- .agents/DEVELOPER_ANNEXATION.md plus numerous investigation notes — potentially overlapping summary/detail layers.
- .agents/GITHUB_ACTIONS_CONTROL.md — intentionally historical evidence plus current control-plane preface; check whether its startup/discovery role is clear.
- autonomic_affairs/docs/next_phase_architecture.md — generic name may obscure whether it is current architecture or historical transitional planning.

## A-040 conclusion

No unresolved high-confidence repository-wide consistency defect remains from this pass. Uncertain memory/context questions are intentionally deferred to A-050 rather than being cleaned speculatively.
