# MSHP-META-A-065 — Restructure task lifecycle storage

## Description

Restructure the agent-task storage model so active task specifications, temporary tracked task knowledge, and archived completed work follow one coherent lifecycle instead of being split between stable task files and a blob-style archive.

The task ID remains the durable identity of a task. Active and archived task material may live in different storage roots; agents should resolve a task by ID from the active task tree and, when absent there, from the archive.

Introduce flexible tracked workspaces for temporary knowledge that must survive task boundaries and agent-context resets but is not necessarily permanent project or agent memory.

## Requirements

- Replace the singular `autonomic_affairs/agent_task_archive.md` model with a structured archive directory under the task system.
- Define and implement a discoverable lookup convention in which task IDs can be resolved from either active task storage or archived task storage.
- Preserve completed task/block structure when archiving rather than flattening specifications into a cumulative archive document.
- When a whole completed block is archived, move its task specifications and block-scoped accompanying workspace material together so their historical relationship remains obvious.
- Preserve established task IDs exactly; archival movement must not rename or renumber tasks.
- Migrate the existing legacy V2 archived history into the new structured archive without losing its established identifiers or recoverability.
- Update active-index archival rules, agent workflow/recovery guidance, navigation, links, and documentation to match the new storage model.
- Introduce tracked temporary workspaces associated with task namespaces/scopes.
- Support at least:
  - task-specific workspace material when useful;
  - block-shared workspace material, e.g. knowledge discovered in one task and needed by later tasks in the same block;
  - broader workstream/specifier-shared workspace material when evidence shows knowledge may be needed across multiple blocks, e.g. `MSHP-THING-B` and `MSHP-THING-F`.
- Treat workspace scoping as a practical convention rather than a rigid bureaucracy: store temporary knowledge at the narrowest convenient shared scope that covers its expected consumers.
- Do not require speculative creation of workspace directories at every supported scope.
- Define the lifecycle of broader-scope workspace material independently from any one block, so archiving an early block does not remove knowledge still needed by later blocks.
- Define how workspace material is handled when its useful lifetime ends: promote durable conclusions where appropriate, archive historically useful leftovers with the relevant completed work, and permit consolidation/pruning when active workspace size becomes a context/token burden.
- Make clear that agents should read only workspace material relevant to the active task rather than automatically ingesting an entire workspace tree.
- Preserve the distinction between:
  - task workspace material: tracked, temporary/intermediate, cross-context working knowledge;
  - `.agents/`: durable agent-facing knowledge with continuing rediscovery value;
  - human-facing docs: durable project architecture/policy;
  - `scratch/`: ignored machine-local mutable state.
- Prefer directory moves and preserved structure over content-merging merely for archival convenience.

## Constraints / non-goals

- Do not create a task database, task-management application, or strict workspace retention bureaucracy.
- Do not require agents to predict the exact future lifetime of every working note.
- Do not promote all investigation output into permanent `.agents/` memory merely because it was expensive to produce.
- Do not delete useful historical workspace material solely because its originating task completed.
- Do not force active agents to load archived or irrelevant workspace material as part of normal task startup.
- Do not change the meaning of Dispatch, lifecycle states, dependencies, or immutable published task IDs except where documentation must be updated to describe storage resolution.
- Do not execute unrelated reminder items while restructuring the task system.

## Acceptance criteria

- There is no longer one growing blob-style archive file acting as the canonical home of archived task history.
- Archived blocks retain individual task specifications and relevant accompanying workspace structure.
- A fresh-context agent can resolve a known task ID without needing to know beforehand whether the task is active or archived.
- Legacy V2 task history remains discoverable under its established IDs.
- The repository documents a flexible workspace scoping model covering task, block, and broader workstream/specifier use without requiring all scopes to exist.
- Cross-block workspace material can remain active while later blocks still need it.
- Agents can distinguish temporary task workspace knowledge from permanent `.agents/` memory and ignored `scratch/` state.
- Workspace material does not become part of mandatory startup context merely by existing.
- Existing active task links, Dispatch semantics, and recovery instructions remain coherent after the migration.
- Relevant current task-system validation/link checks pass.

## Validation

- Traverse every active task-index link and verify its target resolves.
- Verify representative archived task IDs resolve through the documented archive lookup convention, including legacy V2 identifiers.
- Verify a completed block can be represented in the archive with its individual specifications and block workspace intact.
- Verify the documented broader-workspace lifecycle does not require moving cross-block knowledge when only an earlier block completes.
- Search agent/task documentation for obsolete claims that archived task specs never move or that `agent_task_archive.md` is the canonical archive.
- Read the workspace rules from a fresh-context perspective and confirm they do not require indiscriminate workspace ingestion.
- Confirm no executable task, reminder, or durable-memory source has become ambiguous about ownership after the restructuring.
