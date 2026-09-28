# Machine-Soul Hivemind Protocol — Agent Tasks

This is the authoritative **scheduling index** for sufficiently specified executable agent work. Full active task instructions and temporary task workspaces live under [`agent_tasks/`](agent_tasks/); completed task material cycles into its structured [`archive/`](agent_tasks/archive/) without changing task IDs.

Reminders, objectives, and speculative roadmap ideas are not executable work and do not belong in Dispatch.

## Dispatch

_No QUEUED task is currently dispatched._

Dispatch is an ordered authorization/priority list, not a lifecycle state. Only `QUEUED` tasks with satisfied dependencies belong here. Claiming a task changes it to `IN_PROGRESS` and removes it from Dispatch.

## Active task index

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-DEV-A-010`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-010.md) | QUEUED | — | Investigate VS Code annexation | Map VS Code installation, configuration, profiles, extensions, sync, and ownership boundaries for Machine-Soul. |
| [`MSHP-DEV-A-020`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-020.md) | QUEUED | — | Investigate JetBrains and Toolbox annexation | Map Toolbox, IDE installation/versioning, settings, plugins, and ownership boundaries across the JetBrains ecosystem. |
| [`MSHP-DEV-A-030`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-030.md) | QUEUED | — | Investigate Lua multiversion annexation | Investigate sane Windows Lua/LuaJIT side-by-side installation, selection, discovery, uninstall, and version-manager options without preselecting an architecture. |
| [`MSHP-DEV-A-040`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-040.md) | QUEUED | — | Investigate Python multiversion annexation | Investigate Python side-by-side versions, launchers/version managers, install mechanisms, discovery, defaults, and uninstall semantics with multiversion capability preserved. |
| [`MSHP-DEV-A-050`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-050.md) | QUEUED | — | Investigate Node multiversion annexation | Investigate Node.js side-by-side versions and version-manager ecosystems, including npm/Corepack interactions and deterministic version selection. |
| [`MSHP-DEV-A-060`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-060.md) | QUEUED | — | Survey additional runtime candidates | Identify other commonly useful runtimes/toolchains worth future annexation research and classify which deserve deeper investigation without prematurely taskifying all of them. |
| [`MSHP-DEV-A-070`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-070.md) | QUEUED | `MSHP-DEV-A-030`, `MSHP-DEV-A-040`, `MSHP-DEV-A-050`, `MSHP-DEV-A-060` | Synthesize runtime/version-management findings | Compare runtime investigations and identify only the reusable multiversion/version-management abstractions actually justified by evidence. |
| [`MSHP-DEV-A-080`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-080.md) | QUEUED | `MSHP-DEV-A-030` | Investigate LuaRocks annexation | Map LuaRocks installation, Lua-version binding, package trees, scope, package inventory, and coexistence semantics. |
| [`MSHP-DEV-A-090`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-090.md) | QUEUED | `MSHP-DEV-A-040` | Investigate pip annexation | Map pip interpreter binding, user/global/venv scopes, package inventory, and safe Machine-Soul ownership boundaries. |
| [`MSHP-DEV-A-100`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-100.md) | QUEUED | `MSHP-DEV-A-050` | Investigate npm annexation | Map npm installation, Node-version binding, global package scope/prefix, package inventory, and version-manager interactions. |
| [`MSHP-DEV-A-110`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-110.md) | QUEUED | `MSHP-DEV-A-070`, `MSHP-DEV-A-080`, `MSHP-DEV-A-090`, `MSHP-DEV-A-100` | Synthesize runtime package-manager findings | Compare LuaRocks, pip, and npm and identify reusable package-environment/inventory concepts without prematurely implementing unsupported ecosystems. |
| [`MSHP-DEV-A-120`](agent_tasks/MSHP-DEV-A/MSHP-DEV-A-120.md) | QUEUED | `MSHP-DEV-A-010`, `MSHP-DEV-A-020`, `MSHP-DEV-A-070`, `MSHP-DEV-A-110` | Synthesize developer annexation roadmap | Produce evidence-based implementation tasks and structured initiative gaps for editors, IDEs, runtimes, version managers, and runtime package ecosystems. |
| [`MSHP-INST-B-010`](agent_tasks/MSHP-INST-B/MSHP-INST-B-010.md) | COMPLETE | `MSHP-INST-A-040` | Implement scope policy model | Add mutation-side installation scope policy/value types, compatibility semantics, strategy declarations, and cross-account user-scope guards without changing package-manager commands yet. |
| [`MSHP-INST-B-020`](agent_tasks/MSHP-INST-B/MSHP-INST-B-020.md) | COMPLETE | `MSHP-INST-B-010` | Implement scoped installation provenance | Replace one-account-one-app install provenance with scope-aware user/machine ownership records, schema migration, and safe legacy reconciliation primitives. |
| [`MSHP-INST-B-030`](agent_tasks/MSHP-INST-B/MSHP-INST-B-030.md) | COMPLETE | `MSHP-INST-B-020` | Make installation ownership candidate-exact | Refactor install/check/uninstall safety around scoped discovery candidates and exact provenance matching, including post-install scope verification and ambiguity refusal. |
| [`MSHP-INST-B-040`](agent_tasks/MSHP-INST-B/MSHP-INST-B-040.md) | COMPLETE | `MSHP-INST-B-030` | Implement scoped WinGet mutation | Add explicit WinGet user/machine install/list/uninstall scope, dual-scope discovery, exact ownership targeting, and Oh My Posh regression coverage. |
| [`MSHP-INST-B-050`](agent_tasks/MSHP-INST-B/MSHP-INST-B-050.md) | COMPLETE | `MSHP-INST-B-030` | Implement Apt machine scope | Declare Apt as fixed machine scope, use host/machine provenance, and safely reconcile compatible legacy Apt ownership without adding unsupported Linux managers. |
| [`MSHP-INST-B-060`](agent_tasks/MSHP-INST-B/MSHP-INST-B-060.md) | COMPLETE | `MSHP-INST-B-040`, `MSHP-INST-B-050` | Integrate scoped installation lifecycle | Validate scoped install/check/uninstall end to end, update status/docs/initiative coverage, preserve deferred manager gaps, and explicitly clear the Windows config-candidate investigation to resume. |
| [`MSHP-APPS-A-010`](agent_tasks/MSHP-APPS-A/MSHP-APPS-A-010.md) | COMPLETE | — | Investigate Windows config candidates | Inventory Windows-integrated and common Microsoft applications with stable user-manageable configuration surfaces that may deserve Machine-Soul configuration entries. |


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
