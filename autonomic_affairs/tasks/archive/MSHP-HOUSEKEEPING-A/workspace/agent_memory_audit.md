# MSHP-HOUSEKEEPING-A — Agent memory and instruction hygiene audit

Recorded for MSHP-HOUSEKEEPING-A-050.

## Scope reviewed

- Root AGENTS.md.
- All 48 tracked Markdown documents under .agents/.
- .agents/README.md fresh-session reading order and memory-placement rules.
- .agents/WORKFLOW.md recovery, task, claim, CI, archive, authority, knowledge-capture, and history rules.
- .agents/PROVENANCE.md agent-authorship/provenance rules.
- autonomic_affairs/tasks.md plus task-storage/archive navigation.
- autonomic_affairs/reminders.md and initiatives/README.md lifecycle/authorization rules.
- Relevant human-facing governance docs where agent notes delegate authority.

## Method

- Enumerated every .agents document and reviewed its title/headings, task/workspace references, and state-sensitive language.
- Read suspicious/current-control notes in full rather than deciding from keyword matches.
- Scanned all 48 .agents documents after cleanup for retired active-task paths, agent_tasks naming, migration-active wording, until-archival wording, and the obsolete unscoped-WinGet claim.
- Cross-checked source-of-truth and authorization statements across AGENTS.md, .agents/README.md, .agents/WORKFLOW.md, tasks.md, reminders.md, initiatives/README.md, and PROVENANCE.md.

## High-confidence corrections

- Updated live .agents references to moved task research/workspaces so detailed-source pointers resolve under tasks/archive/.
- Updated Windows installation-scope memory to state that INST-B-040 implemented explicit scope-aware WinGet mutation/discovery; retained the earlier limitation only as historical context.
- Updated discovery implementation memory so DISC-A raw research is described as preserved in the archive rather than waiting for archival.
- Updated Python-core memory so legacy state readers are described as deliberate compatibility/recovery support rather than temporary migration-active behavior.
- Marked the legacy-runtime migration audit explicitly historical and recorded that V2-61 completed retirement after parity.
- Added a .agents/README.md rule that dated investigations, migration records, and historical decision snapshots are on-demand references, not startup context.

## Deliberate retention decisions

No .agents document was deleted merely because it is old or overlaps a human-facing document.

Retained as useful current summaries:

- .agents/DEVELOPER_ANNEXATION.md — compact implemented developer-environment map and validation navigation.
- .agents/GITHUB_ACTIONS_CONTROL.md — explicit current control-plane summary plus clearly labeled historical experiment evidence.
- .agents/decisions/main_active_iteration.md — concise branch doctrine not duplicated as mandatory startup content.
- .agents/decisions/git_history_attitude.md — approved direction with an explicit warning that current no-rewrite rules remain authoritative.
- .agents/scrcpy_virtual_screen_manager.md — current tool-specific scar tissue.

Retained as intentionally historical/on-demand evidence:

- dated investigation files under .agents/investigations/;
- v2_stable_baseline.md, which already carries an explicit historical-checkpoint warning;
- runtime_environment_discovery.md and other V2-labelled decisions whose headings/context clearly identify the old checkpoint;
- migration/legacy architecture notes after adding or preserving historical framing.

Architecture notes that overlap human-facing docs were retained because they contain agent-oriented implementation/debugging details and are not part of mandatory startup loading. The new on-demand rule prevents that retained depth from becoming routine context bloat.

## Authority consistency

Verified:

- tasks.md owns scheduling/state/Dispatch in both AGENTS.md and WORKFLOW.md;
- .agents/README.md explicitly excludes live task scheduling from agent memory;
- reminders are non-executable and non-authorizing in both AGENTS.md and reminders.md;
- initiatives are non-executable in AGENTS.md, WORKFLOW.md, and initiatives/README.md;
- additive/no-rewrite history rules agree between AGENTS.md and WORKFLOW.md;
- PROVENANCE.md still contains the registered Gippity designation used by this work;
- fresh-session reading loads only relevant notes/workspaces rather than all .agents material.

## Post-cleanup drift scan

Across all 48 .agents Markdown documents, the targeted scan found zero remaining:

- active-form task-workspace paths of the form autonomic_affairs/tasks/MSHP-.../ for archived blocks;
- agent_tasks references;
- while-migration-is-active compatibility wording;
- until-archival research wording;
- obsolete unscoped-WinGet limitation wording.

## Uncertain or deliberately deferred items

- autonomic_affairs/docs/next_phase_architecture.md has a generic/transitional-looking name, but this audit found no high-confidence basis to delete or rename it. Retained.
- Some dated investigation facts use words such as current relative to their research date. The dated filenames and on-demand loading rule provide context; no speculative freshness rewrite was attempted.
- The repository still has the Agent-facing repository memory hygiene reminder. This one-time audit did not design cadence/triggers/reporting policy for a recurring process, so the reminder remains intentionally open.
- Human review of agent instruction Markdown remains a separate reminder; agent self-audit does not satisfy it.

## Conclusion

All current agent memory/instruction surfaces were deliberately reviewed. High-confidence stale/contradictory content was corrected, startup-context burden was reduced through explicit on-demand guidance, and uncertain/historical knowledge was retained rather than pruned speculatively. No known high-confidence agent-memory defect remains from this pass.
