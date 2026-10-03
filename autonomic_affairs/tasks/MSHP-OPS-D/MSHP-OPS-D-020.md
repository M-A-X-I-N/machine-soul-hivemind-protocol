# MSHP-OPS-D-020 — Implement centralized CI policy engine

## Description

Implement the evidence-backed centralized CI architecture from `workspace/centralized_ci_policy_engine.md`: one small conservative policy job decides which blocking validation and deferred CodeQL units deserve downstream runners for push, pull-request, manual, and scheduled events.

## Requirements

- Use `workspace/centralized_ci_policy_engine.md` as the authoritative design input.
- Evolve the existing `autonomic_affairs/ci_validation_selector.py` into the policy engine rather than creating competing selector logic.
- Use one top-level selector/policy workflow as the **only entry point** for repository CI execution:
  - pushes to `main`;
  - pull requests targeting `main`;
  - `workflow_dispatch`;
  - a daily scheduled reconciliation at `0 6 * * *` (06:00 UTC).
- Keep downstream blocking-validation and CodeQL workflows callable-only (`workflow_call`) so event routing and selection logic exist in one place.
- Run the policy job on `ubuntu-slim`.
- Keep ordinary non-main pushes quiet.
- Compute automatic event change evidence using local Git with event-authoritative SHAs:
  - existing main push: two-dot `before` → `after`;
  - pull request: three-dot base → head / merge-base semantics;
  - manual dispatch: no automatic range; require explicit selection/default all;
  - schedule: run reconciliation against current default-branch `HEAD`, using prior successful check/job history plus the same check relevance mapping used by ordinary automatic selection.
- Fail safe to the complete downstream unit set when:
  - required Git objects/ranges cannot be established;
  - a push is forced or otherwise structurally ambiguous;
  - a path is not recognized by the classifier;
  - classifier/control metadata is malformed;
  - another uncertainty could otherwise suppress useful validation.
- Separate **validation-check selection** from **runner provisioning**:
  - inventory the existing validation commands/steps as stable machine-recognizable check IDs with explicit relevance predicates;
  - select checks at that finer granularity so an unrelated change does not run unrelated checks merely because they share an OS runner;
  - coalesce selected checks onto the minimum practical runner jobs/environments rather than provisioning one runner per small check;
  - keep CodeQL Python and Actions as independently selectable checks.
- Preserve the existing Linux, Windows, fresh-Linux, and fresh-Windows reusable workflows as execution-group starting points, but allow the selector to pass an explicit selected-check set into them (or make an equivalent evidence-backed refactor) so irrelevant steps can be skipped inside an already-needed runner.
- Keep coarse convenience aliases/runner groups available for explicit overrides where useful, but make the canonical automatic/scheduled coverage model check-level rather than only `linux`/`windows`/fresh/CodeQL-level.
- Refactor current CodeQL execution into reusable downstream language analysis so Python and Actions can be selected independently.
- Preserve CodeQL:
  - deferred lifecycle semantics;
  - adaptive scheduled rescanning from the daily 06:00 UTC selector entry point;
  - default query suite;
  - `build-mode: none`;
  - stable per-language categories;
  - least-privilege upload permissions;
  - normal selected-ref manual execution;
  - quiet ordinary non-main pushes.
- Keep `security-events: write` limited to CodeQL call jobs/work rather than the policy job.
- Give the selector job enough read-only GitHub API access to inspect its own prior workflow runs/jobs; prefer the built-in `GITHUB_TOKEN` with least privilege (including `actions: read` and `contents: read`) rather than persistent state or a custom secret.
- Implement scheduled **coverage reconciliation** per downstream check:
  - inspect only prior **successful** executions of that unit;
  - ignore the currently running selector run when looking backward;
  - if no usable prior success exists, consider the unit uncovered and run it;
  - for non-CodeQL validation **checks**, an older successful SHA still covers current `main` when the diff from that SHA to current `HEAD` contains **no path relevant to that check** according to the same classifier/relevance mapping used for push/PR selection;
  - if relevant files changed since that check's last successful covered SHA, select that check;
  - after check selection, coalesce due checks into the smallest practical set of runner jobs;
  - if prior-run history, job identity, or comparison evidence is unavailable/ambiguous, fail safe by running the affected unit rather than assuming coverage.
- Implement scheduled CodeQL reconciliation independently for `codeql-python` and `codeql-actions`:
  - first find the most recent successful execution of that CodeQL unit on the **current main HEAD SHA**;
  - if no successful execution exists on current HEAD, run that CodeQL unit immediately;
  - otherwise determine the age of current main HEAD using repository commit time and the age of that unit's last successful execution on HEAD;
  - while current main HEAD is younger than `24 * 7` hours, the unit is due when its last successful execution on HEAD is at least 24 hours old;
  - once current main HEAD is at least `24 * 7` hours old, the unit is due when its last successful execution on HEAD is at least `24 * 7` hours old;
  - evaluate the two CodeQL units separately so success/failure of one does not falsely cover the other.
- Treat scheduled reconciliation as independent from historical event overrides: `CI: none` or native `skip-checks: true` may suppress an event-triggered run, but they do not permanently mark affected validation as covered; the daily scheduler may later run units whose relevant state remains uncovered.
- Implement conservative automatic classification at minimum for:
  - narrowly allowlisted inert documentation/control text;
  - Python/runtime implementation;
  - install/bootstrap/fresh-clone semantics;
  - executable GitHub Actions/control-workflow semantics;
  - unknown/ambiguous fallback.
- Make classification compositional: union all applicable **check IDs** and then derive the required runner groups from those selected checks.
- Do not treat directory placement or filename resemblance alone as proof that a file is inert/platform-specific.
- Keep the `CI:` control surface but deliberately migrate it to unified policy semantics:
  - no selector on automatic push/PR → automatic classification;
  - `CI: auto` → automatic classification;
  - `CI: all` → all registered checks;
  - `CI: none` → no downstream check, policy job still runs;
  - explicit comma-separated selectors → exactly the named registered checks and/or documented convenience groups, expanded deterministically;
  - `all`, `none`, and `auto` are standalone;
  - duplicates/whitespace may normalize;
  - multiple, unknown, or malformed selectors fail visibly and select all registered checks.
- Preserve native correctly formatted `skip-checks: true` as the harder GitHub-level bypass when no checked-in push/PR workflow should instantiate.
- Validate repository commit/control metadata needed by the policy engine, including current commit-summary grammar and machine-readable control trailers.
- For push/PR events, inspect all newly introduced commits where practical for grammar validation rather than validating only the tip.
- Update current policy/documentation explicitly to supersede OPS-A/OPS-B rules that conflict with the new architecture. Do not leave contradictory live guidance.
- Remove/disable superseded top-level CodeQL routing so one event cannot double-provision equivalent CodeQL analysis.

## Constraints / non-goals

- Do not make changed paths authoritative; they are evidence under a fail-safe classifier.
- Do not use Actions `paths:` / `paths-ignore:` as the CI policy engine.
- Do not silently skip validation for unclassified files.
- Do not make CodeQL advancement-blocking merely because launch policy is centralized.
- Do not drop periodic CodeQL rescanning; replace the fixed weekly-only trigger with the adaptive daily/weekly reconciliation policy above.
- Do not add lower-precision CodeQL query suites, custom queries, path exclusions, model packs, or resource tuning without new evidence.
- Do not add GitHub ruleset configuration in this task; current repository/plan evidence does not justify depending on metadata rulesets.
- Do not add automatic non-main push CI.
- Do not rewrite established Git history.

## Acceptance criteria

- A single small policy job controls check-level relevance decisions and coalesces selected checks into downstream runner jobs.
- The policy job runs on `ubuntu-slim`.
- Push and PR change ranges match documented two-dot/three-dot semantics and fail safe when evidence is unavailable.
- Manual dispatch uses explicit selection rather than inventing an automatic diff.
- Push, PR, manual, and scheduled execution all enter through the same top-level selector/policy workflow.
- The schedule is registered as `0 6 * * *` (06:00 UTC) and runs reconciliation rather than blindly launching downstream work.
- Each CodeQL unit runs immediately when current main HEAD lacks successful coverage, then runs every 24 hours while HEAD is younger than 168 hours and every 168 hours once HEAD is at least 168 hours old.
- Non-CodeQL checks are considered covered across unrelated commits when no check-relevant files changed after their last successful covered SHA, and are selected again when relevant state changed.
- Unrelated checks sharing the same runner environment remain skipped; a Python-only change must not implicitly execute an unrelated Markdown/docs checker merely because both are runnable on Linux.
- Docs-only changes can produce no downstream runners when confidently classified.
- Python/runtime changes select Linux + Windows + Python CodeQL without fresh-clone validation unless fresh-machine semantics are implicated.
- Install/bootstrap changes select all four blocking sets plus relevant CodeQL.
- Central Actions/policy changes conservatively select all four blocking sets plus both CodeQL units.
- Unknown files or malformed policy metadata select the complete registered check set and visibly fail the controller where appropriate.
- Valid `CI:` overrides are authoritative across blocking and CodeQL units.
- `CI: none` still records a successful policy decision while provisioning no downstream runner.
- Native `skip-checks: true` remains distinct and functional.
- CodeQL remains deferred and retains weekly/manual behavior, categories, query policy, build mode, and least-privilege permissions.
- Current authoritative docs contain no surviving contradiction that says changed paths can never influence CI or that `CI:` cannot select CodeQL.
- One integration event does not duplicate blocking or CodeQL execution.

## Validation

- Add deterministic policy-engine tests covering:
  - all selector forms;
  - malformed/multiple selectors;
  - path-to-check relevance unioning;
  - check-to-runner coalescing;
  - unknown fallback;
  - forced/missing-range fallback;
  - docs-only;
  - Python/runtime;
  - install/bootstrap;
  - workflow/control changes;
  - push/PR/manual/schedule event decisions.
- Test local Git range logic with representative commit graphs, including a PR-style merge-base case and a multi-commit push range.
- Run the repository's normal Python policy/unit tests locally/on a suitable runner before cutover.
- Exercise real GitHub workflow behavior for representative cases where practical:
  - docs-only automatic classification;
  - Python/runtime automatic classification;
  - workflow/control automatic classification;
  - valid explicit subset;
  - `CI: none`;
  - invalid selector fail-safe;
  - manual selected-ref execution.
- Verify downstream runner provisioning from the actual job graph/logs, not only selector output text.
- Verify CodeQL Python and Actions can still succeed independently and upload under stable categories.
- Verify the daily `0 6 * * *` schedule remains registered after consolidation and executes against default-branch HEAD.
- Verify scheduled reconciliation can discover prior successful jobs through GitHub run/job history and does not count the current in-progress run.
- Verify CodeQL's 24-hour/168-hour age transitions and current-HEAD requirement deterministically.
- Verify a prior successful non-CodeQL check remains covered across unrelated changes but becomes due after a relevant change.
- Verify unrelated checks sharing a runner are skipped even when another check on that runner is selected.
- Verify ordinary non-main pushes remain quiet.
- Re-read `AGENTS.md`, `.agents/WORKFLOW.md`, and `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md` together after cutover for contradictions.
