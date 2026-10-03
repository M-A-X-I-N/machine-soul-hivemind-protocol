# MSHP-HOUSEKEEPING-A-030 — Canonicalize task-system terminology and paths

## Description

Remove stale task-system naming left behind by the agent_tasks to tasks migration and repair directly related path, link, schema, and explanatory drift.

## Requirements

- Search all tracked text/source files for agent_tasks, agent-tasks, obsolete task paths, stale links into retired task locations, and transitional wording that still describes the old task surface as current.
- Fix high-confidence stale terminology and links.
- Preserve historically intentional mentions when the old name is materially part of a migration/history record; mark them historical where ambiguity would otherwise remain.
- Re-run repository navigation and task lookup checks after edits.

## Constraints / non-goals

- Do not mechanically replace ordinary prose such as agent task when it describes a concept rather than the retired path/name.
- Do not rewrite historical evidence merely to make every old name disappear.
- Do not broaden this task into the full repository weirdness audit; that is MSHP-HOUSEKEEPING-A-040.

## Acceptance criteria

- No live/current authority points agents toward agent_tasks.
- No stale active link/path uses the retired task location.
- Historical references, if retained, are clearly non-authoritative.

## Validation

- Repository-wide text search for retired task-system names/paths.
- Verify task navigation from AGENTS.md, .agents, task docs, reminders, and initiatives.
