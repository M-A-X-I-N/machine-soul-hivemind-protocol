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

### MSHP-AUDIT-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-AUDIT-A-010`](tasks/MSHP-AUDIT-A/MSHP-AUDIT-A-010.md) | QUEUED | — | Add Linux audit command collection | Collect long-lived human-session process execution history with auditd, preserving argv and original `auid` through sudo/root-shell escalation. |

### MSHP-WINGET-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-WINGET-A-010`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-010.md) | QUEUED | — | Investigate Microsoft Store packages through WinGet | Map identity, source, scope, agreements, account/licensing, discovery, ownership, update, and uninstall semantics for `msstore` packages before changing annexation behavior. |
| [`MSHP-WINGET-A-020`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-020.md) | QUEUED | `MSHP-WINGET-A-010` | Investigate custom and non-default WinGet sources | Map source registration, trust, provenance, package identity collisions, lifecycle, restore/remove semantics, and whether source identity must become part of Machine-Soul package ownership. |
| [`MSHP-WINGET-A-030`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-030.md) | QUEUED | `MSHP-WINGET-A-010` | Design a Store-first WinGet package selection policy | Study deterministic Store-first selection without changing WinGet as installation interface. |
| [`MSHP-WINGET-A-040`](tasks/MSHP-WINGET-A/MSHP-WINGET-A-040.md) | QUEUED | `MSHP-WINGET-A-030` | Implement Store-first selection through WinGet | Add scoped Store-first selection after research, validation and explicit thaw. |




### MSHP-CI-PORT-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-CI-PORT-A-010`](tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-010.md) | QUEUED | — | Investigate GitLab CI | GitLab CI. |
| [`MSHP-CI-PORT-A-020`](tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-020.md) | QUEUED | — | Investigate portable or self-hostable CI workflow systems | Portable or self-hostable CI workflow systems. |
| [`MSHP-CI-PORT-A-030`](tasks/MSHP-CI-PORT-A/MSHP-CI-PORT-A-030.md) | QUEUED | `MSHP-CI-PORT-A-010`, `MSHP-CI-PORT-A-020` | Design CI interoperability options | CI interoperability options. |

### MSHP-CI-LAYOUT-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-CI-LAYOUT-A-010`](tasks/MSHP-CI-LAYOUT-A/MSHP-CI-LAYOUT-A-010.md) | QUEUED | — | Relocate exclusively CI-owned scripts into .github | Exclusively CI-owned scripts into .github. |

### MSHP-ANNEX-UPDATE-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-ANNEX-UPDATE-A-010`](tasks/MSHP-ANNEX-UPDATE-A/MSHP-ANNEX-UPDATE-A-010.md) | QUEUED | — | Design safe application update semantics | Safe application update semantics. |
| [`MSHP-ANNEX-UPDATE-A-020`](tasks/MSHP-ANNEX-UPDATE-A/MSHP-ANNEX-UPDATE-A-020.md) | QUEUED | `MSHP-ANNEX-UPDATE-A-010` | Implement a shared update operation with backend pilots | A shared update operation with backend pilots. |

### MSHP-ANNEX-VERIFY-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-ANNEX-VERIFY-A-010`](tasks/MSHP-ANNEX-VERIFY-A/MSHP-ANNEX-VERIFY-A-010.md) | QUEUED | — | Investigate installation manifest origin expectations | Installation manifest origin expectations. |
| [`MSHP-ANNEX-VERIFY-A-020`](tasks/MSHP-ANNEX-VERIFY-A/MSHP-ANNEX-VERIFY-A-020.md) | QUEUED | `MSHP-ANNEX-VERIFY-A-010` | Add origin expectation warnings to supported installers | Origin expectation warnings to supported installers. |

### MSHP-TAKEOVER-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-TAKEOVER-A-010`](tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-010.md) | QUEUED | — | Research adoption and migration of existing installations | Adoption and migration of existing installations. |
| [`MSHP-TAKEOVER-A-020`](tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-020.md) | QUEUED | `MSHP-TAKEOVER-A-010` | Specify takeover planning, consent and rollback contracts | Takeover planning, consent and rollback contracts. |
| [`MSHP-TAKEOVER-A-030`](tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-030.md) | QUEUED | `MSHP-TAKEOVER-A-020` | Implement bounded takeover lifecycle and pilot backends | Bounded takeover lifecycle and pilot backends. |

### MSHP-PKG-RESEARCH-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-PKG-RESEARCH-A-010`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-010.md) | QUEUED | — | Research Flatpak installation and scope lifecycle | Flatpak installation and scope lifecycle. |
| [`MSHP-PKG-RESEARCH-A-020`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-020.md) | QUEUED | — | Research Homebrew and Linuxbrew ownership semantics | Homebrew and Linuxbrew ownership semantics. |
| [`MSHP-PKG-RESEARCH-A-030`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-030.md) | QUEUED | — | Research pipx and user-local application package managers | Pipx and user-local application package managers. |
| [`MSHP-PKG-RESEARCH-A-040`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-040.md) | QUEUED | — | Investigate unmanaged Windows EXE/MSI installer lifecycle | Unmanaged Windows EXE/MSI installer lifecycle. |
| [`MSHP-PKG-RESEARCH-A-050`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-050.md) | QUEUED | — | Investigate Arch/Manjaro package-manager integration | Arch/Manjaro package-manager integration. |
| [`MSHP-PKG-RESEARCH-A-060`](tasks/MSHP-PKG-RESEARCH-A/MSHP-PKG-RESEARCH-A-060.md) | QUEUED | `MSHP-PKG-RESEARCH-A-010`, `MSHP-PKG-RESEARCH-A-020`, `MSHP-PKG-RESEARCH-A-030`, `MSHP-PKG-RESEARCH-A-040`, `MSHP-PKG-RESEARCH-A-050` | Synthesize additional package backend priorities | Additional package backend priorities. |

### MSHP-PLATFORM-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-PLATFORM-A-010`](tasks/MSHP-PLATFORM-A/MSHP-PLATFORM-A-010.md) | QUEUED | — | Audit Windows 11 and Debian/Ubuntu Server support gaps | Windows 11 and Debian/Ubuntu Server support gaps. |
| [`MSHP-PLATFORM-A-020`](tasks/MSHP-PLATFORM-A/MSHP-PLATFORM-A-020.md) | QUEUED | `MSHP-PKG-RESEARCH-A-050` | Plan lower-priority Manjaro/Arch-family support | Lower-priority Manjaro/Arch-family support. |

### MSHP-ANNEX-BULK-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-ANNEX-BULK-A-010`](tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-010.md) | QUEUED | — | Design declarative desired installation sets | Declarative desired installation sets. |
| [`MSHP-ANNEX-BULK-A-020`](tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-020.md) | QUEUED | `MSHP-ANNEX-BULK-A-010` | Add multi-select installation workflow | Multi-select installation workflow. |
| [`MSHP-ANNEX-BULK-A-030`](tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-030.md) | QUEUED | `MSHP-ANNEX-BULK-A-010` | Integrate host-based installation profiles | Host-based installation profiles. |
| [`MSHP-ANNEX-BULK-A-040`](tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-040.md) | QUEUED | `MSHP-ANNEX-BULK-A-020`, `MSHP-ANNEX-BULK-A-030` | Validate fresh-host bulk bootstrap flows | Fresh-host bulk bootstrap flows. |

### MSHP-ANNEX-LAYOUT-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-ANNEX-LAYOUT-A-010`](tasks/MSHP-ANNEX-LAYOUT-A/MSHP-ANNEX-LAYOUT-A-010.md) | QUEUED | — | Design minimal per-application annexation directory layout | Minimal per-application annexation directory layout. |
| [`MSHP-ANNEX-LAYOUT-A-020`](tasks/MSHP-ANNEX-LAYOUT-A/MSHP-ANNEX-LAYOUT-A-020.md) | QUEUED | `MSHP-ANNEX-LAYOUT-A-010` | Migrate shared annexation internals into a dedicated library directory | Shared annexation internals into a clearly separated internal library directory. |

### MSHP-STATE-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-STATE-A-010`](tasks/MSHP-STATE-A/MSHP-STATE-A-010.md) | QUEUED | — | Design durable per-user application-state storage | Durable per-user application-state storage. |
| [`MSHP-STATE-A-020`](tasks/MSHP-STATE-A/MSHP-STATE-A-020.md) | QUEUED | `MSHP-STATE-A-010` | Implement versioned cross-platform state location and migrations | Versioned cross-platform state location and migrations. |
| [`MSHP-STATE-A-030`](tasks/MSHP-STATE-A/MSHP-STATE-A-030.md) | QUEUED | `MSHP-STATE-A-020` | Migrate annexation ownership records and durable action logs | Annexation ownership records and durable action logs. |

### MSHP-LAB-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-LAB-A-010`](tasks/MSHP-LAB-A/MSHP-LAB-A-010.md) | QUEUED | — | Investigate Cloudflare-tunneled workhorse MCP access | Cloudflare-tunneled workhorse MCP access. |
| [`MSHP-LAB-A-020`](tasks/MSHP-LAB-A/MSHP-LAB-A-020.md) | QUEUED | `MSHP-LAB-A-010` | Design shared workhorse scheduling for multiple agents | Shared workhorse scheduling for multiple agents. |
| [`MSHP-LAB-A-030`](tasks/MSHP-LAB-A/MSHP-LAB-A-030.md) | QUEUED | — | Investigate space-efficient multi-branch Git workspaces | Space-efficient multi-branch Git workspaces. |

### MSHP-CI-RUNNER-A

| ID | State | Depends on | Title | Summary |
|---|---|---|---|---|
| [`MSHP-CI-RUNNER-A-010`](tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-010.md) | QUEUED | — | Design nested-virtualized self-hosted CI control plane | Nested-virtualized self-hosted CI control plane. |
| [`MSHP-CI-RUNNER-A-020`](tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-020.md) | QUEUED | `MSHP-CI-RUNNER-A-010` | Research layered VM images and clone-on-write job disks | Layered VM images and clone-on-write job disks. |
| [`MSHP-CI-RUNNER-A-030`](tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-030.md) | QUEUED | `MSHP-CI-RUNNER-A-010`, `MSHP-CI-RUNNER-A-020` | Design a preprovisioned Windows SML worker image | A preprovisioned Windows SML worker image. |
| [`MSHP-CI-RUNNER-A-040`](tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-040.md) | QUEUED | `MSHP-CI-RUNNER-A-010` | Investigate self-hosted-first hosted-runner fallback | Self-hosted-first hosted-runner fallback. |
| [`MSHP-CI-RUNNER-A-050`](tasks/MSHP-CI-RUNNER-A/MSHP-CI-RUNNER-A-050.md) | QUEUED | `MSHP-CI-RUNNER-A-010`, `MSHP-CI-RUNNER-A-020`, `MSHP-CI-RUNNER-A-030`, `MSHP-CI-RUNNER-A-040` | Plan a bounded hybrid-runner proof of concept | A bounded hybrid-runner proof of concept. |

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
