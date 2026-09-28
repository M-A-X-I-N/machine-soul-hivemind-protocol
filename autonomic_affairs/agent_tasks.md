# Machine-Soul Hivemind Protocol — Agent Tasks

This is the authoritative **scheduling index** for sufficiently specified executable agent work. Full active task instructions and temporary task workspaces live under [`agent_tasks/`](agent_tasks/); completed task material cycles into its structured [`archive/`](agent_tasks/archive/) without changing task IDs.

Reminders, objectives, and speculative roadmap ideas are not executable work and do not belong in Dispatch.

## Dispatch

_No QUEUED task is currently dispatched._

Dispatch is an ordered authorization/priority list, not a lifecycle state. Only `QUEUED` tasks with satisfied dependencies belong here. Claiming a task changes it to `IN_PROGRESS` and removes it from Dispatch.

## Active task index

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-META-A-010`](agent_tasks/MSHP-META-A/MSHP-META-A-010.md) | COMPLETE | — | Rename meta namespace | Rename the repository self-management namespace to `autonomic_affairs/` and codify the thematic top-level A convention. |
| [`MSHP-META-A-020`](agent_tasks/MSHP-META-A/MSHP-META-A-020.md) | COMPLETE | `MSHP-META-A-010` | Establish task system | Replace the monolithic ledger with a compact scheduling index, stable detailed task specs, Dispatch, and archival rules. |
| [`MSHP-META-A-030`](agent_tasks/MSHP-META-A/MSHP-META-A-030.md) | COMPLETE | `MSHP-META-A-010` | Genericize machine identities | Remove incidental concrete host/account identities from durable documentation while retaining technically necessary identities. |
| [`MSHP-META-A-040`](agent_tasks/MSHP-META-A/MSHP-META-A-040.md) | COMPLETE | `MSHP-META-A-010` | Formalize agent provenance | Establish stable-designation registry, accurate official identities, optional honorifics, and conspicuous `UNNAMED` behavior. |
| [`MSHP-META-A-050`](agent_tasks/MSHP-META-A/MSHP-META-A-050.md) | COMPLETE | `MSHP-META-A-010` | Establish reminders | Create the non-executable reminders register and seed provenance-rewrite, cross-repo agent-baseline, and Skills investigations. |
| [`MSHP-META-A-060`](agent_tasks/MSHP-META-A/MSHP-META-A-060.md) | COMPLETE | `MSHP-META-A-010` | Codify idiot-maintainer language | Permit optional maintainer-directed idiot-human humor while explicitly excluding end users and formal interfaces. |
| [`MSHP-META-A-065`](agent_tasks/MSHP-META-A/MSHP-META-A-065.md) | COMPLETE | `MSHP-META-A-020` | Restructure task lifecycle storage | Replace the blob-style archive with structured task/block archival and add flexible tracked workspaces for temporary cross-task knowledge. |
| [`MSHP-META-A-070`](agent_tasks/MSHP-META-A/MSHP-META-A-070.md) | COMPLETE | `V2-63` | Rehome assimilation runtime | Move the core Machine-Soul Python runtime and orchestrator out of `accumulated_instruments/` and into the operational `annexation_procedures/` system without redesigning behavior. |
| [`MSHP-META-A-075`](agent_tasks/MSHP-META-A/MSHP-META-A-075.md) | BLOCKED | — | Promote active iteration to main | Promote the current `experimental/v2` iteration to `main`, update active-branch assumptions, and retire the redundant `experimental/v2` branch. |


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
- `COMPLETE`
- `CANCELLED`
- `SUPERSEDED`

A dependency is another task whose completed output is structurally required. A temporary external, technical, or human impediment is a blocker, not a dependency.

### Source ownership

- This index owns task ID, state, dependencies, title, canonical short summary, and Dispatch ordering.
- Individual files under `agent_tasks/` own full execution instructions.
- New-style task specs require: `Description`, `Requirements`, `Constraints / non-goals`, `Acceptance criteria`, and `Validation`; `Blocker` and `Notes` are optional.
- Do not duplicate mutable scheduling facts inside detailed task files.
- Required task instructions use ordinary Markdown headings and links; do not hide them inside rendering-dependent disclosure widgets.

### Storage, workspaces, and archival

Task IDs are permanent identities; their storage location may change as their lifecycle changes. Resolve active tasks under [`agent_tasks/`](agent_tasks/) and archived tasks under [`agent_tasks/archive/`](agent_tasks/archive/). See [`agent_tasks/README.md`](agent_tasks/README.md) for lookup and workspace conventions.

All incomplete tasks and all tasks in active blocks remain in this index. Keep the two most recently completed **new-style blocks** here as context. When an older completed block cycles out, move its block directory intact into `agent_tasks/archive/<block-id>/`, including block/task-scoped workspace material, and remove its rows from this active index. Never archive an incomplete block.

Temporary tracked task knowledge may live in task-, block-, or broader workstream-scoped workspaces. Workspace existence does not make it mandatory startup context; task specifications should point to the pieces they require. Broader workstream workspace material remains active while later blocks still need it.

Completed legacy V2 history is preserved in [`agent_tasks/archive/V2/legacy_v2.md`](agent_tasks/archive/V2/legacy_v2.md). The legacy V2 series is complete and therefore does not appear in the active scheduling table.
