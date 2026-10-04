# Agent instruction and memory router

This directory separates **normative instructions** from **repository memory**.

- `baseline/` contains generic instructions intended to be reusable across repositories.
- `local/` contains MSHP-specific normative instructions. Applicable local rules override conflicting baseline rules.
- `memory/` contains MSHP-specific knowledge, rationale, investigations, decisions, and scar tissue. Memory is not policy and is read only when relevant.

Do not preload this entire directory.

## Read routing

| Situation | Read |
|---|---|
| substantial repository work | `baseline/WORKFLOW.md` + `local/REPOSITORY.md` |
| taskification, Dispatch, claims, task-state changes, recovery | `baseline/WORKFLOW.md` + the authoritative task ledger/spec |
| branch/history/checkpoint/commit operation | `baseline/GIT.md` |
| wholly agent-authored substantive commit | `baseline/PROVENANCE.md` |
| deciding where learned information belongs | `baseline/KNOWLEDGE.md` |
| CI/control-plane work or CI override/diagnosis | `local/CI.md` |
| repository-specific concern | the applicable file under `local/` |
| technical/rationale/history lookup | only relevant file(s) under `memory/` |
| durable project architecture/policy | applicable human-facing documentation |

For a tiny isolated edit, do not load unrelated instruction files merely for ceremony. If the work expands into task-governed, Git-sensitive, provenance-sensitive, CI-sensitive, or knowledge-management work, load the relevant instructions before performing that part.

## MSHP executable-work locations

- ledger / Dispatch / Active claims: `../autonomic_affairs/tasks.md`;
- active task specifications/workspaces: `../autonomic_affairs/tasks/`;
- terminal task archive: `../autonomic_affairs/tasks/archive/`;
- reminders: `../autonomic_affairs/reminders.md`;
- initiatives: `../autonomic_affairs/initiatives/`.

## Memory organization

Current useful memory categories live below `memory/`:

- `architecture/`;
- `decisions/`;
- `investigations/`;
- `platforms/`;
- `tools/`.

Do not create empty taxonomy for appearance. Add categories only when there is actual knowledge to store.

Dated investigations, migration records, and historical decision snapshots are **on-demand references**, not startup context.

Current tracked repository state remains authoritative over remembered conversation context.
