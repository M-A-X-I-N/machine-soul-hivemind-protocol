# Machine-Soul Hivemind Protocol — Agent Tasks

This is the authoritative **scheduling index** for sufficiently specified executable agent work. Full new-style task instructions live in stable linked task files; older completed index entries cycle to [`agent_task_archive.md`](agent_task_archive.md).

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
| [`V2-52`](agent_tasks/legacy_v2.md#v2-52) | COMPLETE | `V2-51` | Define library-first operation architecture | Fix the boundaries between declarations, generic engines, wrappers, orchestration, and exceptional/custom behavior. |
| [`V2-53`](agent_tasks/legacy_v2.md#v2-53) | COMPLETE | `V2-52` | Define atomic wrapper contracts | Specify uniform one-operation wrappers with one importable/executable implementation path and no duplicated business logic. |
| [`V2-54`](agent_tasks/legacy_v2.md#v2-54) | COMPLETE | `V2-52` | Define operation-result model | Define one structured semantic result usable by wrappers, orchestration, tests, automation, and native-process normalization. |
| [`V2-55`](agent_tasks/legacy_v2.md#v2-55) | COMPLETE | `V2-54` | Define native primitive protocol | Specify the narrow versioned JSON/native-process boundary for justified platform primitives. |
| [`V2-56`](agent_tasks/legacy_v2.md#v2-56) | COMPLETE | `V2-53`, `V2-54`, `V2-55` | Define interactive orchestration | Define a broad manager that composes atomic operations but owns no application/platform business logic. |
| [`V2-57`](agent_tasks/legacy_v2.md#v2-57) | COMPLETE | `V2-52`–`V2-56` | Audit legacy implementation | Classify existing Bash/PowerShell behavior into Python policy, declarations, reusable strategies, custom hooks, primitives, or deletion. |
| [`V2-58`](agent_tasks/legacy_v2.md#v2-58) | COMPLETE | `V2-57` | Implement Python core | Build generic discovery, dispatch, config/state/backup/account/install/result/primitive libraries with contract tests. |
| [`V2-59`](agent_tasks/legacy_v2.md#v2-59) | COMPLETE | `V2-58` | Convert application declarations | Represent the current application set with `_application.py` definitions plus minimal justified hooks. |
| [`V2-60`](agent_tasks/legacy_v2.md#v2-60) | COMPLETE | `V2-58`, `V2-59` | Replace operations with wrappers | Replace application operation implementations with tiny Python wrappers around declarations and shared engines. |
| [`V2-61`](agent_tasks/legacy_v2.md#v2-61) | IN_PROGRESS | `V2-58`, `V2-60` | Reduce native scripts | Retain only justified native Bash/PowerShell primitives and retire superseded policy/orchestration code after parity. |
| [`V2-62`](agent_tasks/legacy_v2.md#v2-62) | QUEUED | `V2-56`, `V2-60`, `V2-61` | Implement orchestrator | Build the interactive manager over the same atomic operations and common results used by direct execution. |
| [`V2-63`](agent_tasks/legacy_v2.md#v2-63) | QUEUED | `V2-58`–`V2-62` | Validate end to end | Migrate/expand tests, prove Windows/Linux/fresh-clone parity, then remove stale legacy remnants. |

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

### Archival

All incomplete tasks and all tasks in active blocks remain in this index. Keep the two most recently completed **new-style blocks** here as context. When an older completed block cycles out, move only its index entries to [`agent_task_archive.md`](agent_task_archive.md), ordered by block completion time. Never archive an incomplete block, and never relocate/delete detailed task files merely because their index entries archived.

Completed legacy V2 history is preserved in [`agent_tasks/legacy_v2.md`](agent_tasks/legacy_v2.md) and referenced from the archive. While V2 remains incomplete, only V2-52 through V2-63 appear in the active table.
