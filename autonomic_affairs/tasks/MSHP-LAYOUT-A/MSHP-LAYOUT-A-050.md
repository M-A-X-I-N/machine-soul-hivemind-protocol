# MSHP-LAYOUT-A-050 — Validate and consolidate the normalized repository layout

## Description

Perform the cross-cutting validation/cleanup pass after the baseline and MSHP directory migrations.

## Requirements

- Audit live tracked files for stale references to:
  - `project/` as the baseline control namespace;
  - `autonomic_affairs/`;
  - `annexation_procedures/`;
  - `assimilation_directives/`;
  - `accumulated_instruments/`;
  - `acquired_intelligence/`;
  - `arcane_experiments/`;
  - `assembled_assets/`;
  - `abandoned_artifacts/`.
- Distinguish stale operational/navigation references from truthful historical mentions in archived task/research evidence.
- Update the MSHP layout policy and root README to describe the final normalized topology.
- Verify baseline/local ownership boundaries still hold after the `meta/` migration.
- Verify `.machine_soul_root` remains documented/tested as the stable repository-root sentinel.
- Run the broadest practical validation needed to prove imports, tests, CI routing, docs/navigation, and task recovery are coherent after the path migration.

## Constraints / non-goals

- Do not rewrite archived historical prose solely to erase old names.
- Do not redesign working subsystems unrelated to path fallout.
- Do not add compatibility aliases/symlink directories unless a real external dependency proves one is required.

## Acceptance criteria

- Final live top-level vocabulary is:
  - `meta/`
  - `annexation/`
  - `assimilation/`
  - `tools/`
  - `research/`
  - `experiments/`
  - `assets/`
  - `archive/`
  - plus externally/conventionally required dot/directories such as `.agents/`, `.github/`, and ignored `scratch/`.
- Live source, tests, workflows, instructions, and navigation contain no unresolved dependencies on superseded paths.
- Relevant test/CI validation succeeds.
- The block can be archived without leaving duplicate layout authority.

## Validation

- Repository-wide path/reference audit with archived-history exceptions reviewed intentionally.
- Relevant Python, shell/matrix/session, and CI selector/control-plane tests.
- Baseline-managed blob comparison against `M-A-X-I-N/baseline`.
- Fresh navigation/recovery walkthrough using `meta/tasks.md`.
