# MSHP-META-A-020 — Establish the canonical agent-task index/detail/archive system

## Description

Replace the monolithic task ledger with a compact scheduling index plus stable per-task execution specifications and an archive that removes old completed work from the active view without deleting information.

## Requirements

- `autonomic_affairs/agent_tasks.md` owns Dispatch plus the compact columns `ID`, `State`, `Depends on`, `Title`, and canonical short `Summary`.
- Detailed new-style specifications live at `autonomic_affairs/agent_tasks/<block-id>/<task-id>.md`.
- Required task-spec sections are `Description`, `Requirements`, `Constraints / non-goals`, `Acceptance criteria`, and `Validation`; `Blocker` and `Notes` are optional.
- The index owns mutable scheduling facts such as state/dependencies; task files own execution instructions.
- Canonical task instructions use ordinary Markdown headings/links rather than HTML disclosure blocks.
- New IDs use `<project>[-<specifier>...]-<block>-<number>`; this repository uses project ID `MSHP`.
- Blocks use A-Z then AA/AB if required. Numbers are three digits, normally allocated by tens; insertions consume free integers.
- Published IDs are immutable. If insertion space becomes absurdly exhausted, restructure unpublished/remaining work into another block rather than renumbering published IDs.
- Lifecycle states are `QUEUED`, `IN_PROGRESS`, `BLOCKED`, `FROZEN`, `COMPLETE`, `CANCELLED`, and `SUPERSEDED`.
- `NEXT` is not a state. Dispatch is the ordered authorization/priority mechanism.
- Dependencies are completed-task requirements; runtime/external/human impediments are blockers.
- Keep the two most recently completed new-style blocks represented in the active index; archive older completed-block index entries by completion time.
- Detailed task files stay at stable paths permanently when their index entries archive.
- Preserve every established `V2-*` ID. Keep the legacy definitions in `agent_tasks/legacy_v2.md`; expose only incomplete V2 tasks in the active index.
- Update agent/recovery/navigation instructions to the new system.

## Constraints / non-goals

- Do not invent a task-tracking application, database, or complex reminder schema.
- Do not duplicate mutable state/dependency metadata between index and detailed task files.
- Do not renumber legacy V2 tasks or new published IDs.

## Acceptance criteria

- A fresh-context agent can skim one small table, see Dispatch, and click a task ID for all execution detail.
- Completed legacy V2 history remains recoverable without occupying the active table.
- New-style task specs have stable paths.
- Archive rules are documented and do not break links.
- The active index contains all incomplete tasks plus the currently active new-style block.

## Validation

- Read every index link and verify its target exists.
- Verify every Dispatch ID exists in the table and is `QUEUED` with satisfied dependencies.
- Verify no root/agent instruction still expects the old monolithic/Next-task workflow.
- Verify legacy V2-52 through V2-63 remain discoverable under their original IDs.
