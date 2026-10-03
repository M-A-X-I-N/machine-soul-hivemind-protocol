# Machine-Soul Hivemind Protocol — Tasks

This is the authoritative **scheduling index** for sufficiently specified executable agent work. Full non-terminal task instructions and temporary task workspaces live under [`tasks/`](tasks/); terminal task blocks live in the structured [`archive/`](tasks/archive/) without changing task IDs.

Reminders, objectives, and speculative roadmap ideas are not executable work and do not belong in Dispatch.

## Dispatch

1. [`MSHP-HOUSEKEEPING-A-040`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-040.md) — audit repository-wide consistency and weirdness.

Dispatch is an ordered authorization/priority list, not a lifecycle state. Only `QUEUED` tasks with satisfied dependencies belong here. Claiming a task changes it to `IN_PROGRESS`, removes it from Dispatch, and records a live claim below.

## Active claims

Claims are live coordination locks, not identity or recovery credentials. The task table remains authoritative for lifecycle state; this section records who currently owns active execution.

| Task | Lineage | Canonical branch | Claimed at (UTC) | Notes |
|---|---|---|---|---|

## Active task index

Task rows are grouped by block for readability. Every block uses the same authoritative scheduling schema; headings are presentation only and do not change task identity, dependency, state, claim, or Dispatch semantics.

### MSHP-WINGET-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-WINGET-A-010`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-010.md) | FROZEN | — | Investigate Microsoft Store packages through WinGet | Map identity, source, scope, agreements, account/licensing, discovery, ownership, update, and uninstall semantics for `msstore` packages before changing annexation behavior. |
| [`MSHP-WINGET-A-020`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-020.md) | FROZEN | `MSHP-WINGET-A-010` | Investigate custom and non-default WinGet sources | Map source registration, trust, provenance, package identity collisions, lifecycle, restore/remove semantics, and whether source identity must become part of Machine-Soul package ownership. |


### MSHP-HOUSEKEEPING-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-HOUSEKEEPING-A-010`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-010.md) | COMPLETE | — | Establish housekeeping freeze boundary | Make HOUSEKEEPING-A the only executable workstream, keep every pre-existing incomplete block frozen, and inventory terminal/frozen/tasks/reminders/initiatives/agent-memory surfaces for cleanup. |
| [`MSHP-HOUSEKEEPING-A-020`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-020.md) | COMPLETE | `MSHP-HOUSEKEEPING-A-010` | Archive all terminal task blocks | Move every dead/done pre-housekeeping block intact into the task archive and replace the rolling-two-completed-block retention rule with archive-all-terminal-blocks. |
| [`MSHP-HOUSEKEEPING-A-030`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-030.md) | COMPLETE | `MSHP-HOUSEKEEPING-A-020` | Canonicalize task-system terminology and paths | Remove stale `agent_tasks` naming, retired task paths, links, and transitional task-system wording while preserving intentional historical references. |
| [`MSHP-HOUSEKEEPING-A-040`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-040.md) | QUEUED | `MSHP-HOUSEKEEPING-A-030` | Audit repository-wide consistency and weirdness | Inspect tracked repository material for high-confidence stale, contradictory, duplicated, misleading, broken, or obsolete references and fix cautiously. |
| [`MSHP-HOUSEKEEPING-A-050`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-050.md) | QUEUED | `MSHP-HOUSEKEEPING-A-040` | Audit agent memory and instruction hygiene | Cautiously review all agent-facing memory/instructions for stale, duplicated, contradictory, or unnecessarily burdensome context, retaining uncertain material. |
| [`MSHP-HOUSEKEEPING-A-060`](tasks/MSHP-HOUSEKEEPING-A/MSHP-HOUSEKEEPING-A-060.md) | QUEUED | `MSHP-HOUSEKEEPING-A-050` | Close and self-archive housekeeping | Revalidate the cleaned repository, archive HOUSEKEEPING-A itself, release all housekeeping coordination state, and leave the next reminder candidate unstarted. |


## Task contract

### Identity

New task IDs use:

```text
<project>[-<specifier>...]-<block>-<number>
```

This repository uses `MSHP`. Specifiers are optional workstream namespaces and should be used sparingly. Blocks use `A`–`Z`, then `AA`, `AB`, etc. Numbers are exactly three digits, normally allocated in tens (`010`, `020`, ...). Insertions consume free integers between published tasks. Published IDs are immutable; if insertion space becomes ridiculous, restructure remaining unpublished work into a new block rather than renumbering established tasks.

Legacy `V2-*` IDs are permanent and are never translated into new IDs.

### States

Allowed lifecycle states:

- `QUEUED`
- `IN_PROGRESS`
- `BLOCKED`
- `FROZEN`
- `AWAITING_DEFERRED_CI`
- `COMPLETE`
- `CANCELLED`
- `SUPERSEDED`

A dependency is another task whose completed output is structurally required. A temporary external, technical, or human impediment is a blocker, not a dependency. `FROZEN` is an intentional priority/policy hold rather than a technical blocker. `AWAITING_DEFERRED_CI` means implementation and advancement-blocking validation are complete while explicitly deferred analysis is still pending; such a task is not `COMPLETE` until its required deferred checks pass.

### Source ownership

- This index owns task ID, state, dependencies, title, canonical short summary, and Dispatch ordering.
- Individual files under `tasks/` own full execution instructions.
- New-style task specs require: `Description`, `Requirements`, `Constraints / non-goals`, `Acceptance criteria`, and `Validation`; `Blocker` and `Notes` are optional.
- Do not duplicate mutable scheduling facts inside detailed task files.
- Required task instructions use ordinary Markdown headings and links; do not hide them inside rendering-dependent disclosure widgets.

### Storage, workspaces, and archival

Task IDs are permanent identities; their storage location may change as their lifecycle changes. Resolve active tasks under [`tasks/`](tasks/) and archived tasks under [`tasks/archive/`](tasks/archive/). See [`tasks/README.md`](tasks/README.md) for lookup and workspace conventions.

All non-terminal tasks remain in this index. Once every task in a block is terminal (`COMPLETE`, `CANCELLED`, or `SUPERSEDED`), move the block directory intact into `tasks/archive/<block-id>/`, including block/task-scoped workspace material, and remove its rows from this active index. Never archive a block that still contains any non-terminal task.

Temporary tracked task knowledge may live in task-, block-, or broader workstream-scoped workspaces. Workspace existence does not make it mandatory startup context; task specifications should point to the pieces they require. Broader workstream workspace material remains active while later blocks still need it.

Completed legacy V2 history is preserved in [`tasks/archive/V2/legacy_v2.md`](tasks/archive/V2/legacy_v2.md). The legacy V2 series is complete and therefore does not appear in the active scheduling table.
