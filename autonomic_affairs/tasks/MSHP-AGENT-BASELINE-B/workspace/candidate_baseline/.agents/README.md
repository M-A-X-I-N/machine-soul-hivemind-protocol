# Agent instruction and memory router

This directory separates **normative instructions** from **repository memory**.

- `baseline/` contains generic instructions shared across repositories.
- `local/` contains repository-specific instructions. Applicable local instructions override conflicting baseline instructions.
- `memory/` contains repository-specific knowledge. Memory is not policy and is read only when relevant.

Do not preload this entire directory.

## Read routing

| Situation | Read |
|---|---|
| substantial repository work | `baseline/WORKFLOW.md` and `local/REPOSITORY.md` |
| taskification, Dispatch, claims, task-state changes, recovery | `baseline/WORKFLOW.md` |
| branch/history/checkpoint/commit operation | `baseline/GIT.md` |
| wholly agent-authored substantive commit | `baseline/PROVENANCE.md` |
| deciding where learned information belongs | `baseline/KNOWLEDGE.md` |
| repository-specific concern | the applicable file under `local/` |
| technical/rationale/history lookup | only the relevant file(s) under `memory/` |
| executable work | the authoritative task ledger and linked task/spec/workspace identified by local policy |
| durable project architecture/policy | applicable human-facing documentation |

For a tiny isolated edit, do not load unrelated instruction files merely for ceremony. If the work expands into task-governed, Git-sensitive, provenance-sensitive, or knowledge-management work, load the relevant instructions before performing that part.

Current tracked repository state remains authoritative over remembered conversation context.
