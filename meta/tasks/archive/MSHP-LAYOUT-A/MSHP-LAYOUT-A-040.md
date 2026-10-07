# MSHP-LAYOUT-A-040 — Normalize generic support-directory names

## Description

Reduce thematic/meme naming for generic repository domains while preserving their placement contracts.

## Requirements

Rename:

- `accumulated_instruments/` → `tools/`
- `acquired_intelligence/` → `research/`
- `arcane_experiments/` → `experiments/`
- `assembled_assets/` → `assets/`
- `abandoned_artifacts/` → `archive/`

Update live documentation, routing, scripts, tests, CI path rules, and navigation accordingly.

Keep the intended meanings:

- `tools/` — standalone reusable utilities/programs not intrinsically part of annexation/assimilation;
- `research/` — durable technical research/references/discoveries that are not canonical project architecture or agent memory;
- `experiments/` — active prototypes/proofs/reverse-engineering harnesses;
- `assets/` — inert/static reusable resources;
- `archive/` — inactive/decommissioned material retained outside Git history because it still has practical historical value.

## Constraints / non-goals

- Do not move canonical project architecture out of `meta/docs/`.
- Do not conflate `research/` with `.agents/memory/`; the latter remains agent-facing non-normative memory.
- Do not conflate root `archive/` with `meta/tasks/archive/`; their parent scopes define different meanings.
- Do not populate currently empty directories merely because they were renamed.

## Acceptance criteria

- All five new directory names exist with their prior contents preserved.
- Live placement/navigation policy uses the new names.
- No active tooling or CI rule relies on the old generic support-directory names.

## Validation

- Compare moved tree/blob identities where content did not otherwise require edits.
- Search live files for stale path dependencies.
- Verify tool entrypoints under `tools/` still operate from their new location where applicable.
