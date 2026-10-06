# Task storage

This directory contains the durable task specifications and tracked working context behind the compact scheduling index at [`../tasks.md`](../tasks.md).

## Task lookup

A task ID is the durable identity. Its pathname may change when completed work is archived.

For a known task ID:

1. look for its active block/specification under this directory;
2. if it is no longer active, look under [`archive/`](archive/);
3. use the archive navigation for legacy formats or historical exceptions.

New-style non-terminal tasks normally use `tasks/<block-id>/<task-id>.md`. Once every task in a block is terminal (`COMPLETE`, `CANCELLED`, or `SUPERSEDED`), the block moves intact to `tasks/archive/<block-id>/`. Task IDs never change merely because storage moves.

The legacy `V2-*` series predates per-task files and is preserved monolithically under `archive/V2/`.

## Tracked temporary workspaces

Workspaces hold intermediate knowledge that must survive task boundaries or agent-context resets but is not necessarily permanent project memory. Use the narrowest **convenient** shared scope and do not create empty workspace taxonomy speculatively.

Typical shapes are:

```text
tasks/<block-id>/workspace/
tasks/<block-id>/workspace/<task-id>/
tasks/<workstream-prefix>/workspace/
```

The last form is for knowledge intentionally shared across multiple blocks, for example `MSHP-THING-B` and `MSHP-THING-F`. Exact nesting is a convention, not a schema.

Task specifications should link workspace material they actually require. Agents should **not** ingest an entire workspace tree merely because it exists.

## Workspace lifecycle

Task- and block-scoped workspace material travels with its block when that block is archived.

Broader workstream/specifier-scoped workspace material has an independent lifetime. Keep it active while any expected later block still needs it; when the wider scope is finished, promote durable conclusions and archive or retire the remaining historical working material as appropriate.

Before material leaves active use, promote durable human-facing architecture into normal docs, continuing expensive-to-rediscover agent knowledge into `.agents/memory/`, and let source/tests remain authoritative for implemented behavior. Preserve useful historical leftovers with their archived scope. Consolidate or prune active workspace material when its size creates context/token burden.

Workspace material is tracked temporary/intermediate knowledge. It is distinct from permanent `.agents/memory/` knowledge and ignored machine-local `scratch/` state.

## Archival

The active scheduling index keeps non-terminal work only. When every task in a block is terminal, move the block intact under `archive/` and remove its rows from the active index. Archival preserves structure rather than merging specs and notes into a growing document; no rolling completed-block context is retained in the active task surface.
