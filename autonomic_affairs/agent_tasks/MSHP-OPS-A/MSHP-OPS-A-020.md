# MSHP-OPS-A-020 — Refactor repository validation into reusable sets

## Description

Extract the existing Machine-Soul validation surface into coherent reusable GitHub Actions workflows/validation sets without changing what a full validation run proves.

## Requirements

- Inventory the current checked-in validation workflow and preserve every existing Linux, Windows, and fresh-clone check unless a concrete redundancy is demonstrated and documented.
- Choose a small coherent set of stable validation-set names based on what the checks prove, not on changed-file paths.
- Implement each validation set as reusable workflow machinery callable through `workflow_call` or an equivalently native GitHub Actions reuse mechanism.
- Preserve runner/platform requirements and test commands exactly unless a task-local improvement is required for reuse.
- Keep a composition that represents full repository validation and is behaviorally equivalent to the pre-refactor suite.
- Make the registered validation-set names easy for the later dispatcher and humans to select explicitly.
- Keep existing automatic `main` validation functioning until the dispatcher/cutover task replaces it; do not create a period where main silently loses validation.
- Record any GitHub-managed analysis that is outside the checked-in validation workflows (currently including enabled CodeQL/default code scanning when observable) as separate from these blocking validation sets so it can follow the deferred-CI policy.

## Constraints / non-goals

- Do not implement changed-path routing.
- Do not change main/non-main trigger policy yet except where strictly necessary to stage reusable workflows safely.
- Do not optimize away tests merely to reduce runner minutes.
- Do not convert GitHub-managed CodeQL/default setup into advanced setup unless a concrete requirement emerges.

## Acceptance criteria

- Every pre-existing Machine-Soul validation check belongs to a named reusable validation set.
- A full composition executes the same effective validation surface as before the refactor.
- Individual validation sets can be invoked independently by the next task.
- Main remains protected from an accidental validation gap during the staged refactor.

## Validation

- Validate workflow syntax/structure through GitHub Actions using the smallest useful checkpoint.
- Run the full pre-existing validation surface at least once against the refactored composition before considering behavior preserved.
- Compare job/step coverage with the previous `.github/workflows/machine_soul_validation.yml`.
