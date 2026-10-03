# MSHP-OPS-C-060 — Migrate agent_tasks naming to tasks

## Description

Execute the approved generic-task naming migration using the design from C-050 with unusually strong recoverability.

## Requirements

- Perform the path/name migration in recoverable checkpoints on a fresh authorized lineage.
- Update all tracked links, agent instructions, scripts, tests, archive/workspace references, and source-of-truth wording.
- Preserve permanent task IDs and historical meaning.
- Validate startup, task lookup, Dispatch, claims, archives, and recovery after the final tree is coherent.

## Constraints / non-goals

- Do not rewrite historical commits solely to rename old references.
- Do not integrate a half-renamed tree to `main`.
- Do not use the contaminated Lyra namespace.

## Acceptance criteria

- The repository uses generic `tasks` naming consistently.
- No live links/parsers/recovery instructions still depend on obsolete paths except intentional historical text.
- Fresh agent startup/recovery works from the renamed structure.

## Validation

- Run repository-wide stale-reference searches.
- Run affected tests/parsers/link checks and a fresh-start recovery walkthrough.
