# Machine-Soul Hivemind Protocol — Tasks

This is the authoritative **scheduling index** for sufficiently specified executable agent work. Full non-terminal task instructions and temporary task workspaces live under [`tasks/`](tasks/); terminal task blocks live in the structured [`archive/`](tasks/archive/) without changing task IDs.

Reminders, objectives, and speculative roadmap ideas are not executable work and do not belong in Dispatch.

## Dispatch

_No QUEUED task is currently dispatched._

Dispatch is an ordered authorization/priority list, not a lifecycle state. Only `QUEUED` tasks with satisfied dependencies belong here. Claiming a task changes it to `IN_PROGRESS`, removes it from Dispatch, and records a live claim below.

## Active claims

Claims are live coordination locks, not identity or recovery credentials. The task table remains authoritative for lifecycle state; this section records who currently owns active execution.

| Task | Lineage | Canonical branch | Claimed at (UTC) | Notes |
|---|---|---|---|---|

## Active task index

Task rows are grouped by block for readability. Every block uses the same authoritative scheduling schema; headings are presentation only and do not change task identity, dependency, state, claim, or Dispatch semantics.

### MSHP-LAYOUT-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-LAYOUT-A-010`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-010.md) | COMPLETE | — | Rename the generic baseline project-control namespace to meta | Move the baseline-reserved control namespace from exact lowercase `project/` to exact lowercase `meta/`, then adopt the changed generic baseline into MSHP. |
| [`MSHP-LAYOUT-A-020`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-020.md) | COMPLETE | `MSHP-LAYOUT-A-010` | Move the MSHP control plane to meta | Move the complete `autonomic_affairs/` control plane to `meta/` while preserving task authority, archives, docs/tests, CI-control helpers, and root discovery. |
| [`MSHP-LAYOUT-A-030`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-030.md) | COMPLETE | `MSHP-LAYOUT-A-020` | Shorten the Machine-Soul functional trees | Rename `annexation_procedures/` → `annexation/` and `assimilation_directives/` → `assimilation/`, updating runtime/import/configuration references without semantic redesign. |
| [`MSHP-LAYOUT-A-040`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-040.md) | COMPLETE | `MSHP-LAYOUT-A-030` | Normalize generic support-directory names | Rename the generic thematic support directories to `tools/`, `research/`, `experiments/`, `assets/`, and `archive/` while preserving their placement contracts. |
| [`MSHP-LAYOUT-A-050`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-050.md) | COMPLETE | `MSHP-LAYOUT-A-040` | Validate and consolidate the normalized repository layout | Audit stale paths, update final layout/navigation docs, validate tests/CI/task recovery, and confirm the normalized topology is coherent end-to-end. |
| [`MSHP-LAYOUT-A-060`](tasks/MSHP-LAYOUT-A/MSHP-LAYOUT-A-060.md) | COMPLETE | `MSHP-LAYOUT-A-050` | Reconcile MSHP fully against the canonical baseline | Perform a dedicated post-migration consumer-conformance pass against `M-A-X-I-N/baseline`, correcting generic drift or policy leakage while preserving MSHP-owned state. |

### MSHP-WINGET-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-WINGET-A-010`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-010.md) | FROZEN | — | Investigate Microsoft Store packages through WinGet | Map identity, source, scope, agreements, account/licensing, discovery, ownership, update, and uninstall semantics for `msstore` packages before changing annexation behavior. |
| [`MSHP-WINGET-A-020`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-020.md) | FROZEN | `MSHP-WINGET-A-010` | Investigate custom and non-default WinGet sources | Map source registration, trust, provenance, package identity collisions, lifecycle, restore/remove semantics, and whether source identity must become part of Machine-Soul package ownership. |



## Task contract

### Identity

New task IDs use:

```text
<project>[-<specifier>...]-<block>-<number>
```

This repository uses `MSHP`. Specifiers are optional workstream namespaces and should be used sparingly. Blocks use `A`–`Z`, then `AA`, `AB`, etc. Numbers are exactly three digits, normally allocated in tens (`010`, `020`, ...). Insertions consume free integers between published tasks. Published IDs are immutable; if insertion space becomes ridiculous, restructure remaining unpublished work into a new block rather than renumbering established tasks.

Legacy `V2-*` IDs are permanent and are never translated into new IDs.

### Lifecycle semantics

The generic lifecycle, state meanings, Dispatch/claim behavior, dependency-vs-blocker distinction, deferred validation, and terminal advancement rules are defined by [`.agents/baseline/WORKFLOW.md`](../.agents/baseline/WORKFLOW.md).

This index records the current state; it does not duplicate those semantics.

### Source ownership

- This index owns task ID, state, dependencies, title, canonical short summary, and Dispatch ordering.
- Individual files under `tasks/` own full execution instructions.
- New-style task specs require: `Description`, `Requirements`, `Constraints / non-goals`, `Acceptance criteria`, and `Validation`; `Blocker` and `Notes` are optional.
- Do not duplicate mutable scheduling facts inside detailed task files.
- Required task instructions use ordinary Markdown headings and links; do not hide them inside rendering-dependent disclosure widgets.

### Storage and archival

Task IDs are permanent identities; storage location may change with lifecycle.

- active task specs/workspaces: [`tasks/`](tasks/);
- terminal blocks: [`tasks/archive/`](tasks/archive/);
- lookup/workspace/archive conventions: [`tasks/README.md`](tasks/README.md).

All non-terminal tasks remain in this index. Archive only when the entire block is terminal, as defined by the baseline workflow.

Completed legacy V2 history remains in [`tasks/archive/V2/legacy_v2.md`](tasks/archive/V2/legacy_v2.md).
