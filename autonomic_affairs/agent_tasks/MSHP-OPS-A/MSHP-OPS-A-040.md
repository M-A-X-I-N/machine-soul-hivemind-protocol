# MSHP-OPS-A-040 — Validate CI control plane and thaw developer work

## Description

Prove the new agent-branch and CI-control model end to end, reconcile deferred GitHub analysis, cut over without redundant runners, and restore the DEV-B workstream at the exact pre-freeze checkpoint.

## Requirements

- Verify the canonical executing lineage and its `agent/{identifier}/main` branch remain recoverable from repository state/history.
- Demonstrate the normal development loop on an agent branch with no automatic blocking CI after an ordinary push.
- Demonstrate explicit manual validation against an agent branch/ref for at least one selected validation set and for full blocking validation.
- Demonstrate a main push with no `CI:` override dispatches every registered blocking validation set exactly once.
- Demonstrate explicit main selection semantics for a subset and for `CI: none` without using path-based routing.
- Demonstrate malformed/unknown selectors fail safe rather than suppressing validation.
- Confirm GitHub-managed CodeQL/code-scanning behavior as actually enabled in repository settings and classify its checks under the deferred-CI policy without unnecessarily converting default setup.
- Exercise `AWAITING_DEFERRED_CI` on a real task/checkpoint when a genuinely deferred check is pending; do not manufacture waiting when all deferred checks have already completed.
- Ensure no legacy workflow trigger remains that duplicates dispatcher-launched jobs.
- Update recovery/agent notes with any expensive-to-rediscover Actions behavior discovered during implementation.
- After the OPS-A control plane is proven, restore the frozen DEV-B checkpoint:
  - `MSHP-DEV-B-070` returns to `IN_PROGRESS` unless repository evidence shows its implementation completed while frozen;
  - `MSHP-DEV-B-080`, `MSHP-DEV-B-090`, and `MSHP-DEV-B-100` return to their pre-freeze `QUEUED` states unless their dependencies/state have legitimately changed;
  - repopulate Dispatch only for genuinely eligible/authorized queued work, preserving any already-claimed in-progress task.
- Leave the repository ready to resume normal development under the new branch/CI model.

## Constraints / non-goals

- Do not rewrite or squash the granular implementation history merely to produce a tidy cutover.
- Do not spend CI solely to reduce a numeric usage target; every verification run in this task should prove a specific control-plane behavior.
- Do not leave the DEV-B workstream frozen once the new model is demonstrably operational.
- Do not infer validation selection from paths.

## Acceptance criteria

- Actual GitHub Actions history demonstrates the documented main and agent-branch defaults/overrides.
- Full blocking validation passes under the new dispatcher.
- Deferred-CI state semantics are usable against the repository's real analysis checks.
- Duplicate/obsolete triggers are gone.
- DEV-B scheduling state is restored faithfully and normal task progression can resume.

## Validation

- Inspect workflow runs/jobs for each exercised routing case.
- Run the full blocking validation suite through the new dispatcher.
- Inspect CodeQL/code-scanning checks/settings available to the agent and document limitations honestly.
- Reread task ledger, Dispatch, workflow docs, and active refs after thaw for consistency.
