# MSHP-OPS-B-020 — Integrate advanced CodeQL with selective-CI policy

## Description

Apply the evidence-backed MSHP CodeQL architecture from the OPS-B investigation: keep CodeQL as a separate deferred security-analysis workflow while aligning its routing, concurrency, permissions, and manual branch behavior with the repository's established CI philosophy.

Use `workspace/codeql_advanced_setup.md` as the authoritative investigation/synthesis input.

## Requirements

- Preserve the existing advanced-mode workflow as the foundation.
- Keep automatic CodeQL on pushes to `main`, pull requests targeting `main`, and the existing weekly schedule.
- Add `workflow_dispatch` so CodeQL can be explicitly run against a selected agent/non-main ref.
- Keep ordinary non-main branch pushes quiet.
- Add concurrency grouped by workflow + event type + ref with `cancel-in-progress: true`.
- Keep explicit `actions` + `python`, `build-mode: none`, `fail-fast: false`, Ubuntu runners, and stable per-language categories.
- Keep one stable automatic query policy using the built-in default suite.
- Reduce permissions to `contents: read` and `security-events: write`.
- Do not add a separate CodeQL config file while there is no persistent config-only policy.
- Do not add CodeQL analysis path filters while scans already report complete coverage.
- Replace generic generated-template comments with concise MSHP-specific rationale where useful.
- Update durable CI policy/docs so CodeQL is explicitly deferred: blocking validation may permit advancement while CodeQL is pending, but required CodeQL success remains part of task completion when applicable.
- Preserve native `skip-checks: true` behavior; do not invent a CodeQL-specific skip token.

## Constraints / non-goals

- Do not register CodeQL as a normal blocking validation set.
- Do not add automatic `security-extended` or `security-and-quality` profiles.
- Do not create multiple persistent CodeQL configurations merely to offer profile choices.
- Do not use changed paths to decide whether CodeQL launches.
- Do not restrict analysis coverage without a measured problem.
- Do not add custom queries, packs, models, query filters, resource tuning, custom DB locations, or alternate CodeQL tool versions.
- Do not convert the single workflow into reusable-workflow machinery without a second real caller.
- Do not rewrite the maintainer's historical advanced-mode commit.

## Acceptance criteria

- Main pushes, PRs to main, and weekly scheduling remain automatic CodeQL entry points.
- Manual dispatch is exposed for explicit branch/ref analysis.
- Ordinary agent-branch pushes remain CodeQL-quiet.
- Concurrency cancels only superseded runs in the same event/ref lifecycle.
- `actions` and `python` remain separate `build-mode: none` analyses with stable categories.
- Default queries and full current coverage are preserved.
- Workflow permissions are reduced without breaking analysis/upload.
- Repository policy clearly treats CodeQL as deferred rather than blocking CI.
- No unnecessary config file, path filter, additional query profile, or extra analysis origin is introduced.

## Validation

- Verify an ordinary implementation-branch push does not launch CodeQL.
- Integrate the final workflow checkpoint to `main` with normal Machine-Soul validation explicitly limited appropriately for a CI/docs-only change; allow CodeQL itself to run.
- Verify both `Analyze (python)` and `Analyze (actions)` succeed after permission reduction.
- Verify logs still report complete current extraction coverage.
- Verify GitHub registers the workflow with `workflow_dispatch`.
- If the current agent tool surface cannot initiate manual dispatch, document that limitation instead of manufacturing a substitute; rely on GitHub's documented selected-ref semantics and record the exact manual UI/CLI path.
- Verify no extra CodeQL configuration/category origin was introduced.
- Reread CI policy and workflow together for contradictions before completion.
