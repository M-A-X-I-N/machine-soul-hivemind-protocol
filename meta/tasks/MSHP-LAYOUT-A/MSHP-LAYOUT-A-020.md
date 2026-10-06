# MSHP-LAYOUT-A-020 — Move the MSHP control plane to meta

## Description

Replace the MSHP-specific `autonomic_affairs/` name with the baseline-aligned exact lowercase `meta/` control-plane path.

## Requirements

- Move the complete live `autonomic_affairs/` tree to `meta/`, preserving task IDs, archive/workspace structure, docs, tests, CI-control helpers, reminders, and initiatives.
- Update root `AGENTS.md`, local agent routing/policy, README navigation, GitHub workflow references, scripts, tests, documentation links, and any live code that refers to the old path.
- Preserve task authority and recoverability while the active task system moves its own physical location.
- Keep `.machine_soul_root` unchanged as the runtime repository-root sentinel.
- Preserve historical meaning in archived evidence; do not rewrite historical prose merely to make old names disappear unless a live link/path must change.

## Constraints / non-goals

- Do not rename `annexation_procedures/`, `assimilation_directives/`, or the generic support directories in this task.
- Do not change task IDs or lifecycle semantics.
- Do not collapse docs/tests/helpers merely because the parent directory is changing.

## Acceptance criteria

- `meta/` owns the MSHP repository/project control plane.
- No live authoritative instruction, workflow, script, or test depends on `autonomic_affairs/`.
- The task ledger remains authoritative and usable at `meta/tasks.md`.
- Archived task blocks remain structurally intact.
- Root discovery still uses `.machine_soul_root` and is unaffected by the control-plane rename.

## Validation

- Verify task/claim/Dispatch routing through the new path.
- Search non-archival live files for stale `autonomic_affairs/` dependencies.
- Run the relevant control-plane/path-sensitive tests and CI selection validation.
- Verify `.machine_soul_root` discovery tests still pass.
