# MSHP-AGENT-BASELINE-B-020 — Generic extraction traceability

## Purpose

Map the current MSHP instruction surface to the candidate generic baseline or to explicitly non-generic destinations before any live refactor.

## Root AGENTS.md

| Current section | Destination | Treatment |
|---|---|---|
| Repository identity intro | local `REPOSITORY.md` + tiny root orientation | MSHP-specific mission stays local; root keeps only tiny universally useful orientation. |
| Before substantive work | candidate root `AGENTS.md` + candidate `.agents/README.md` | Generic read-order/routing retained; hardcoded MSHP paths removed. |
| Source-of-truth ownership | baseline `WORKFLOW.md` + local `REPOSITORY.md` | Generic authority principle retained; actual MSHP paths/owners remain local. |
| Top-level directory contract | local `REPOSITORY.md` | Entirely MSHP-specific. |
| Knowledge retention policy | baseline `KNOWLEDGE.md` | Generic retention/placement rules retained and made instruction-vs-memory explicit. |
| Configuration safety laws | local `REPOSITORY.md` | Entirely Machine-Soul product policy. |
| Agent working branches | baseline `WORKFLOW.md` + `GIT.md` | Generic lineage/recovery model retained. |
| Centralized CI behavior | local `CI.md` | MSHP-specific check selection/cadence/IDs stay local. |
| Git and checkpoint discipline | baseline `GIT.md` + `WORKFLOW.md` | Generic history/checkpoint/task-boundary semantics retained. |
| Commit messages | baseline `GIT.md` | Generic bracketed grammar/kinds retained. |
| Provenance pointer | baseline `PROVENANCE.md` | Full policy retained generically. |
| Working style: native mechanisms | local `REPOSITORY.md` | Engineering preference is currently tied to MSHP machine-management work. |
| Working style: shared runtime vs adapters | local `REPOSITORY.md` | MSHP implementation architecture. |
| Working style: declarative host/account/platform exceptions | local `REPOSITORY.md` | MSHP architecture preference. |
| Documentation style / internal humor | local policy or durable human doc pointer | Repository-specific human-facing style currently lives in MSHP docs; not required baseline kernel. |
| No ceremonial validation | baseline `WORKFLOW.md` | Generic. |
| Fresh clone reconstruction goal | local `REPOSITORY.md` | Machine-Soul product goal. |

## Current .agents/README.md

| Current concern | Destination | Treatment |
|---|---|---|
| `.agents` combines procedure and memory | replaced by candidate router | New architecture separates baseline/local instructions from memory. |
| Expensive-to-rediscover knowledge retention | baseline `KNOWLEDGE.md` | Retained. |
| What does not belong in agent memory | baseline `KNOWLEDGE.md` + local paths | Generic exclusions retained; MSHP-specific paths localize. |
| Current category tree | future `.agents/memory/` | Categories become memory-only, not peer siblings of normative instructions. |
| Do not create empty taxonomy | baseline `KNOWLEDGE.md` | Retained. |
| Prefer updating existing note / mark uncertainty | baseline `KNOWLEDGE.md` | Retained. |
| Historical investigations on demand | baseline `KNOWLEDGE.md` | Retained. |
| Fresh-session order | candidate root + router | Converted from “read workflow/provenance every time” to trigger-based routing. |

## Current .agents/WORKFLOW.md

| Current section | Destination | Treatment |
|---|---|---|
| Checkpoint discipline | baseline `WORKFLOW.md` + `GIT.md` | Retained, path-neutral. |
| Task granularity | baseline `WORKFLOW.md` | Retained. |
| Terminal block archival | baseline `WORKFLOW.md` | Semantics retained; physical paths delegated to local task contract. |
| Agent lineages/working branches | baseline `WORKFLOW.md` | Retained. |
| Active task claims | baseline `WORKFLOW.md` | Retained. |
| CI selection/deferred validation | split | Generic `AWAITING_DEFERRED_CI` / `FROZEN` lifecycle remains in WORKFLOW; concrete MSHP selector/check/cadence behavior goes to local `CI.md`. |
| Interrupted-session recovery | baseline `WORKFLOW.md` + local paths | Retained, path-neutral. |
| Source-of-truth discipline | baseline `WORKFLOW.md` + local `REPOSITORY.md` | Generic precedence retained; concrete source map local. |
| Knowledge capture | baseline `KNOWLEDGE.md` | Retained. |
| Git history preservation | baseline `GIT.md` | Retained. |
| Validation | baseline `WORKFLOW.md` | Retained. |
| Provenance | baseline router/provenance | Retained without old relative paths. |
| Initiatives | baseline `WORKFLOW.md` | Generic non-executable semantics retained; local files/paths supplied by repository policy. |

## Current .agents/PROVENANCE.md

The policy is broadly reusable across the maintainer's repositories and becomes candidate baseline `PROVENANCE.md`.

Changes made during extraction:

- language no longer says “canonical policy for this repository”; it is a baseline policy;
- the registry is described as maintainer-wide rather than project-local;
- commit-summary grammar moves to `GIT.md`;
- current identity examples tied to the authoring moment are removed from normative policy;
- `Gippity` / `UNNAMED` registry semantics and honorific rules remain intact.

## Generic behavior added explicitly during extraction

These were already part of the established collaboration workflow but were not fully centralized in the old tracked instructions:

- once a bounded task/range is authorized, progress autonomously through ordinary checkpoints;
- interrupt only for genuine human-policy/architecture ambiguity, destructive authority, human-only information, or validation failure that cannot be responsibly resolved;
- do not repeatedly ask permission between tasks that the human explicitly authorized as a range;
- do not start beyond that authorized range merely because the next task exists;
- local instructions explicitly override conflicting baseline instructions;
- absence of a local override leaves baseline policy active;
- memory is structurally non-normative and demand-loaded.

These additions are not MSHP product behavior; they are the workflow behavior the baseline is intended to preserve.

## Explicitly non-generic material

The candidate baseline intentionally contains none of the following:

- `autonomic_affairs/` path names;
- Machine-Soul thematic directory names;
- configuration/symlink safety laws;
- MSHP CI workflow/check IDs or schedule;
- MSHP application/runtime/install architecture;
- MSHP documentation-style path;
- current tasks/reminders/initiatives;
- existing MSHP memory/investigation content.

## Candidate tree

The B-020 candidate lives under:

```text
workspace/candidate_baseline/
├── AGENTS.md
└── .agents/
    ├── README.md
    └── baseline/
        ├── WORKFLOW.md
        ├── GIT.md
        ├── PROVENANCE.md
        └── KNOWLEDGE.md
```

B-030 owns the complementary local/memory candidate and the migration map for current MSHP-specific material.
