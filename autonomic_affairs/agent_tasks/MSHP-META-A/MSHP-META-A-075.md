# MSHP-META-A-075 — Promote active iteration to main

## Description

Make `main` the ordinary active development/experimental branch again by promoting the then-current `experimental/v2` state to `main` and removing the now-redundant `experimental/v2` branch.

The repository does not need a permanently separate experimental branch merely because the current architecture is still evolving. `main` may represent the current experiment. If a future v3-style redesign needs branch separation, the then-current iteration may be preserved or moved aside at that time.

## Requirements

- Re-check the current relationship between `main` and `experimental/v2` immediately before promotion.
- Promote the complete then-current `experimental/v2` state to `main`.
- Prefer a normal fast-forward update when the commit graph permits it.
- The human has explicitly authorized changing `main` to the `experimental/v2` lineage for this promotion. If intervening work makes a non-fast-forward ref move necessary, stop and verify that no unexpected unique work has appeared on `main`; preserve any such work before exercising that narrow authorization.
- Verify `main` points to the intended promoted commit before deleting any branch.
- Delete the remote `experimental/v2` branch only after successful promotion and verification.
- Preserve `experimental/v1` unless separately instructed otherwise.
- Update README, agent guidance, architecture/status notes, CI configuration, task/recovery documentation, and other current references that incorrectly describe `experimental/v2` as the active branch or `main` as intentionally inactive/clean.
- Preserve genuinely historical references to `experimental/v2` where the branch name is part of the historical record rather than current guidance.
- Ensure future task execution and recovery procedures naturally operate from `main` after the promotion.
- Keep the repository's default branch as `main`.

## Constraints / non-goals

- Do not rename `main` to a versioned branch.
- Do not delete `experimental/v1`.
- Do not rewrite commit history merely to make the branch promotion aesthetically cleaner.
- Do not create an `experimental/v3` branch or otherwise pre-design a future iteration scheme.
- Do not alter runtime/application behavior as part of this branch-management task.
- Do not discard unique commits if branch state differs from the expected relationship at execution time.

## Acceptance criteria

- `main` contains the complete intended current Machine-Soul iteration.
- `experimental/v2` no longer exists as a remote branch.
- `experimental/v1` remains preserved.
- Current documentation and agent instructions identify `main` as the active branch and do not instruct agents to work on `experimental/v2`.
- Historical discussion may still mention `experimental/v2` where appropriate.
- Task/recovery workflow remains coherent after the branch change.
- Relevant CI succeeds on the promoted `main` head.

## Validation

- Compare `main` and `experimental/v2` immediately before mutation and record/inspect whether promotion is fast-forward-safe.
- After promotion, verify the `main` head SHA equals the intended former `experimental/v2` head SHA.
- Run or observe the relevant CI on `main` and require success before considering the task complete.
- Verify the remote branch list contains `main` and preserved `experimental/v1` but not `experimental/v2`.
- Search current documentation, agent instructions, workflows, and task/recovery guidance for stale active-branch references to `experimental/v2`; classify remaining matches as intentionally historical.
- Confirm no unique pre-promotion `main` work was lost.
