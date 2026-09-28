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
| [`MSHP-META-A-075`](agent_tasks/MSHP-META-A/MSHP-META-A-075.md) | COMPLETE | — | Promote active iteration to main | Promote the former `experimental/v2` iteration to `main`, update active-branch assumptions, and leave the old v2 ref retained but operationally ignored. |
| [`MSHP-DISC-A-010`](agent_tasks/MSHP-DISC-A/MSHP-DISC-A-010.md) | COMPLETE | `MSHP-META-A-070` | Define discovery semantics | Separate installation, applied-configuration, and effective-configuration discovery into explicit concepts with shared result semantics and extension boundaries. |
| [`MSHP-DISC-A-020`](agent_tasks/MSHP-DISC-A/MSHP-DISC-A-020.md) | COMPLETE | `MSHP-DISC-A-010` | Investigate installation discovery | Determine how granular installation existence, mechanism, provenance, location, version, scope, ownership, and ambiguity can be discovered across supported platforms. |
| [`MSHP-DISC-A-030`](agent_tasks/MSHP-DISC-A/MSHP-DISC-A-030.md) | COMPLETE | `MSHP-DISC-A-010` | Investigate effective configuration | Determine how each current application can prove, infer, or fail to verify that the intended configuration is actually being consumed. |
| [`MSHP-DISC-A-040`](agent_tasks/MSHP-DISC-A/MSHP-DISC-A-040.md) | COMPLETE | `MSHP-DISC-A-010` | Normalize applied configuration checks | Make `check_config` rigorously report structural deployment state without conflating it with runtime effectiveness. |
| [`MSHP-DISC-A-050`](agent_tasks/MSHP-DISC-A/MSHP-DISC-A-050.md) | COMPLETE | `MSHP-DISC-A-020`, `MSHP-DISC-A-030`, `MSHP-DISC-A-040` | Synthesize discovery roadmap | Distill investigation results, preserve durable findings, and create the executable implementation tasks justified by the discovered architecture. |
| [`MSHP-DISC-B-010`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-010.md) | COMPLETE | `MSHP-DISC-A-050` | Implement discovery assessment model | Add typed observations, evidence strength, installation candidates/assessments, and configuration-verification assessments beneath OperationResult. |
| [`MSHP-DISC-B-020`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-020.md) | COMPLETE | `MSHP-DISC-B-010` | Decouple installation discovery | Give applications explicit installation-discovery plans independent from install/uninstall strategies and route check_installed through a shared assessment engine. |
| [`MSHP-DISC-B-030`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-030.md) | COMPLETE | `MSHP-DISC-B-020` | Implement Linux installation discovery | Add rich Linux package/executable discovery and wire current Linux applications to granular candidate assessments. |
| [`MSHP-DISC-B-040`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-040.md) | COMPLETE | `MSHP-DISC-B-020` | Implement native Windows installation discovery | Add WinGet correlation, ARP/MSI, MSIX/AppX, executable/version, and built-in capability discovery for current native Windows applications. |
| [`MSHP-DISC-B-050`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-050.md) | IN_PROGRESS | `MSHP-DISC-B-020` | Implement Windows POSIX installation discovery | Discover Bash/Zsh/Fish inside the same MSYS2/Cygwin-style compatibility environment targeted by their Windows configuration. |
| [`MSHP-DISC-B-060`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-060.md) | QUEUED | `MSHP-DISC-B-010` | Establish verify_config operation | Add the distinct effective-configuration operation, wrapper/capability plumbing, verification plans, and shared evidence aggregation without app-specific probes yet. |
| [`MSHP-DISC-B-070`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-070.md) | QUEUED | `MSHP-DISC-B-050`, `MSHP-DISC-B-060` | Implement shell startup verification | Add reusable controlled startup-trace verification for Bash, Zsh, and Fish on Linux and supported Windows POSIX environments. |
| [`MSHP-DISC-B-080`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-080.md) | QUEUED | `MSHP-DISC-B-040`, `MSHP-DISC-B-060` | Implement native config verification | Add honest resolution/application-native verification for PowerShell, CMD, Windows Terminal, and Contour. |
| [`MSHP-DISC-B-090`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-090.md) | QUEUED | `MSHP-DISC-B-070`, `MSHP-DISC-B-080` | Implement Oh My Posh verification | Verify OMP theme usability and actual consumer-shell selection using application and runtime evidence without conflating the two. |
| [`MSHP-DISC-B-100`](agent_tasks/MSHP-DISC-B/MSHP-DISC-B-100.md) | QUEUED | `MSHP-DISC-B-030`, `MSHP-DISC-B-040`, `MSHP-DISC-B-050`, `MSHP-DISC-B-070`, `MSHP-DISC-B-080`, `MSHP-DISC-B-090` | Integrate discovery status | Present installation, structural configuration, and effective configuration together in orchestration/machine output and validate the full discovery architecture end to end. |


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
