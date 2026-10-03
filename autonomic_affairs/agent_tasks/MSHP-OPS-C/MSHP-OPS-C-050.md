# MSHP-OPS-C-050 — Design the agent_tasks to tasks migration

## Description

Prepare a recoverable repository-wide rename from agent-specific task naming to generic `tasks` naming after claim/ledger structure is settled.

## Requirements

- Inventory every tracked/untracked-by-design reference to `agent_tasks`, including docs, links, scripts, tests, recovery instructions, archive/workspace conventions, and CI utilities.
- Choose final names/paths for the ledger and task directory, expected to be `autonomic_affairs/tasks.md` and `autonomic_affairs/tasks/` unless evidence shows a real agent/tooling problem.
- Design migration checkpoints, compatibility/transition handling if needed, and validation before changing paths.
- Identify any concurrent-branch/recovery hazards from the rename.

## Constraints / non-goals

- Do not perform the rename in this task.
- Do not retain `agent_` merely from inertia; retain it only if a concrete benefit is discovered.
- Do not invent a separate human task namespace without need.

## Acceptance criteria

- A complete migration map and validation plan exists.
- Every known reference class is accounted for.
- The following implementation task can execute without rediscovering the blast radius.

## Validation

- Repository-wide searches plus parser/test inspection.
- Reread startup/recovery paths against the plan.
