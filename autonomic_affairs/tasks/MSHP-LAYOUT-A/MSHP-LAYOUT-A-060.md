# MSHP-LAYOUT-A-060 — Reconcile MSHP fully against the canonical baseline

## Description

After the repository layout migration is complete, perform a dedicated consumer-conformance pass to ensure MSHP still follows the current canonical contract in `M-A-X-I-N/baseline`.

This task is intentionally separate from A-050: A-050 proves the renamed MSHP repository is internally coherent; A-060 proves MSHP remains a correct baseline consumer.

## Requirements

- Re-inspect the current `M-A-X-I-N/baseline` repository rather than relying on remembered baseline state.
- Compare the complete baseline-managed generic surface against MSHP using the manual maintenance procedure in `.agents/baseline/MAINTENANCE.md`.
- Reconcile any generic drift so MSHP's baseline-managed files match the intended canonical baseline content.
- Verify repository-specific policy exists only in repository-owned surfaces and has not leaked into baseline-managed files.
- Verify MSHP's local instruction router accurately describes its final post-migration paths and subject triggers.
- Verify the exact lowercase top-level `meta/` integration path follows the canonical baseline contract while retaining MSHP-owned task/docs/tests/control-plane contents.
- Verify root `AGENTS.md`, local policy, memory routing, task authority, reminders/initiatives, and baseline maintenance routing compose correctly.
- Review any controlled differences between the baseline template seed and MSHP's repository-owned files as intentional local ownership rather than accidental drift.
- Preserve MSHP-specific architecture and naming under local ownership; conformity does not mean copying template seed state over live MSHP state.
- Correct any stale generic documentation in MSHP that still describes the pre-`meta/` baseline contract.

## Constraints / non-goals

- Do not overwrite MSHP task/reminder/initiative state with template seed state.
- Do not force repository-owned files to be byte-identical to template seed files.
- Do not introduce version manifests, updater state, or automated synchronization.
- Do not redesign unrelated MSHP functionality during the conformity pass.
- Do not rewrite historical archived evidence solely to erase obsolete path names.

## Acceptance criteria

- Every baseline-managed file in MSHP matches the intended canonical file in `M-A-X-I-N/baseline`.
- No MSHP-specific normative policy remains hidden in baseline-managed files.
- MSHP's repository-owned instruction/control surfaces accurately describe the final normalized layout.
- Exact lowercase `meta/` is used consistently as the baseline project-control integration path.
- Root → generic router → local router → task/memory/meta navigation is coherent from a fresh-session perspective.
- The final repository satisfies the manual baseline maintenance/adoption contract without relying on hidden exceptions.
- Any remaining differences from the baseline repository are explicitly attributable to repository-owned content.

## Validation

- Blob/content comparison of all baseline-managed files between `M-A-X-I-N/baseline@main` and MSHP.
- Semantic review of root `AGENTS.md`, `.agents/local/*`, `.agents/memory/` routing, and `meta/` ownership.
- Search generic baseline-managed files for MSHP-specific names/paths/policy leakage.
- Search MSHP local routing/docs for stale pre-migration baseline control-path references.
- Fresh navigation walkthrough from root `AGENTS.md` through generic/local/task/memory surfaces.
- Record the final conformance result durably before closing/archive of the block.
