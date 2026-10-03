# MSHP-OPS-C — `agent_tasks` → `tasks` migration design

## Decision

Rename the active task system to generic task terminology:

- `autonomic_affairs/agent_tasks.md` → `autonomic_affairs/tasks.md`
- `autonomic_affairs/agent_tasks/` → `autonomic_affairs/tasks/`
- `agent_tasks/archive/` → `tasks/archive/`
- task/block/workstream `workspace/` structure remains otherwise unchanged
- published task IDs remain unchanged

No concrete agent/tooling benefit was found for retaining the `agent_` prefix. Tasks are repository executable work and may naturally be owned/executed by agents without encoding that executor into the storage name.

## Inventory

At C-050 design time:

- the task system contains 101 tracked files and 22 directory/tree entries beneath the old task root, plus the root ledger file;
- repository code search finds 39 files containing `agent_tasks` references;
- no Python, CI workflow, or other executable parser was found that depends on the current path or on one monolithic task table;
- affected reference classes are startup/recovery docs, task-system navigation, `.agents` memory/investigations, initiatives/reminders, current task specifications, and archived historical task documents.

## Migration rules

1. **Atomic authority cutover.** The final coherent tree must contain `tasks.md` + `tasks/` and must not retain `agent_tasks.md` or `agent_tasks/` as aliases/stubs.
2. **No dual authority.** Do not leave redirect files, symlinks, duplicate ledgers, compatibility directories, or two task roots.
3. **Preserve identity and structure.** Task IDs, block IDs, archive layout, workspace scopes, Dispatch, Active claims, states, dependencies, and summaries are unchanged except for links/paths needed by the rename.
4. **Update live authority everywhere.** Root `AGENTS.md`, `.agents/README.md`, `.agents/WORKFLOW.md`, root/autonomic READMEs, initiatives, reminders, current task specs, and any agent-memory notes that point at the current task system must use the new names.
5. **Historical prose may remain historical.** Archived specs/notes may retain literal `agent_tasks` wording only when explicitly describing the old system as historical fact. Navigational links or statements of current authority inside historical material must still point at the new current paths where useful.
6. **Relative links move with their files.** Internal links that remain structurally correct after the subtree rename need not be rewritten merely for churn; path-sensitive links to the ledger/root must be updated.
7. **No main half-state.** Construct and validate the renamed tree on the authorized Sera lineage. Integrate only a coherent final cutover tree to `main`.

## Suggested implementation checkpoints

These checkpoints belong on the Sera lineage; only the final coherent tree should reach `main`.

### Checkpoint A — prepare content rewrites

- update current authoritative docs/recovery instructions from `agent_tasks` to `tasks`;
- update all task-ledger links from `agent_tasks/...` to `tasks/...`;
- update task-system README/navigation text for the new names;
- update non-historical `.agents`, initiatives, reminders, and current task specs;
- classify remaining old-name hits as intentional historical prose or bugs.

Checkpoint A may temporarily refer to future paths on the agent branch; do not integrate it alone.

### Checkpoint B — atomic filesystem move

- move the ledger blob to `autonomic_affairs/tasks.md`;
- recreate every file under `autonomic_affairs/tasks/` using the existing blob where content is unchanged and rewritten blobs where content changed;
- remove `autonomic_affairs/agent_tasks.md` and the old `autonomic_affairs/agent_tasks/` subtree in the same resulting tree;
- preserve Git history additively; the move is represented by ordinary commit/tree history, not a history rewrite.

### Checkpoint C — validation/fixup

- verify `autonomic_affairs/tasks.md` exists and old ledger does not;
- verify `autonomic_affairs/tasks/README.md` and representative active/archive/workspace task paths resolve;
- verify every row/claim/Dispatch link in the ledger resolves;
- search the final tree for `agent_tasks` / `agent-task`; classify every remaining hit as intentionally historical or fix it;
- verify required startup/recovery docs contain no live old path;
- verify frozen WinGet and queued OPS-D task states survive unchanged;
- verify the Active-claims row still points to Sera/C-060 while implementation is active, then release it when C-060 completes.

## Concurrent-work and recovery hazards

- Branches created before the rename may still contain old task paths. Their existence does not authorize adoption and does not justify restoring the old names.
- Authorized recovery of such a branch must compare it with current `main` and reconcile task-system changes explicitly.
- If unrelated concurrent work advances `main` during C-060, preserve both histories. Unrelated file changes can be merged additively; any concurrent edits to task/recovery surfaces are a stop/reconciliation condition rather than an automatic merge.
- The already-contaminated Lyra namespace remains unrelated and must not be repurposed for this migration.

## Validation target

A fresh-context agent should be able to read `AGENTS.md`, follow the new `autonomic_affairs/tasks.md` path, inspect Dispatch/Active claims, resolve active or archived task IDs through `autonomic_affairs/tasks/README.md`, and recover authorized work without encountering a live reference to the old task-system path.
## C-060 completion validation

Validated on the coherent renamed tree after the filesystem cutover and historical-design fixup:

- `autonomic_affairs/tasks.md` exists; the former `autonomic_affairs/agent_tasks.md` path does not;
- `autonomic_affairs/tasks/` exists; no path containing `agent_tasks` remains in the current recursive tree;
- all 41 unique live Markdown task links emitted by the ledger resolve to paths present in the current tree;
- required startup/recovery surfaces (`AGENTS.md`, `.agents/README.md`, `.agents/WORKFLOW.md`, root `README.md`, and `autonomic_affairs/README.md`) contain no live `agent_tasks.md` / `agent_tasks/` references;
- the only intentionally retained old-path wording found by the stale-reference sweep is historical prose in archived task-system material, e.g. `MSHP-META-A-020`, which documents the old contract that actually existed;
- the C-050 migration workspace was restored after an over-broad preparatory replacement had temporarily turned its old→new examples into self-referential `tasks → tasks` text;
- both `MSHP-WINGET-A` tasks remain `FROZEN`;
- `MSHP-OPS-D-010` remains `QUEUED` and undispatched;
- Active claims continued to identify only `MSHP-OPS-C-060` / `sera_261003-192400` until this completion checkpoint.

Fresh-start walkthrough result: a new agent can now follow `AGENTS.md` → `.agents/WORKFLOW.md` → `autonomic_affairs/tasks.md` → linked active/archived task storage under `autonomic_affairs/tasks/README.md` without encountering a live dependency on the former task-system path.
