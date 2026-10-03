# MSHP-OPS-D-020 — Implement centralized CI policy engine

## Description

Implement the evidence-backed centralized CI architecture from `workspace/centralized_ci_policy_engine.md`: one small conservative policy job decides which blocking validation and deferred CodeQL units deserve downstream runners for push, pull-request, manual, and scheduled events.

## Requirements

- Use `workspace/centralized_ci_policy_engine.md` as the authoritative design input.
- Evolve the existing `autonomic_affairs/ci_validation_selector.py` into the policy engine rather than creating competing selector logic.
- Use one top-level workflow as the policy/event control plane for:
  - pushes to `main`;
  - pull requests targeting `main`;
  - `workflow_dispatch`;
  - the existing weekly CodeQL schedule.
- Run the policy job on `ubuntu-slim`.
- Keep ordinary non-main pushes quiet.
- Compute automatic event change evidence using local Git with event-authoritative SHAs:
  - existing main push: two-dot `before` → `after`;
  - pull request: three-dot base → head / merge-base semantics;
  - manual dispatch: no automatic range; require explicit selection/default all;
  - schedule: select the two CodeQL units only.
- Fail safe to the complete downstream unit set when:
  - required Git objects/ranges cannot be established;
  - a push is forced or otherwise structurally ambiguous;
  - a path is not recognized by the classifier;
  - classifier/control metadata is malformed;
  - another uncertainty could otherwise suppress useful validation.
- Register six downstream policy units:
  - `linux`;
  - `windows`;
  - `fresh-linux`;
  - `fresh-windows`;
  - `codeql-python`;
  - `codeql-actions`.
- Preserve the existing four reusable blocking-validation workflows as downstream units unless implementation evidence requires a narrower mechanical refactor.
- Refactor current CodeQL execution into reusable downstream language analysis so Python and Actions can be selected independently.
- Preserve CodeQL:
  - deferred lifecycle semantics;
  - weekly security rescan;
  - default query suite;
  - `build-mode: none`;
  - stable per-language categories;
  - least-privilege upload permissions;
  - normal selected-ref manual execution;
  - quiet ordinary non-main pushes.
- Keep `security-events: write` limited to CodeQL call jobs/work rather than the policy job.
- Implement conservative automatic classification at minimum for:
  - narrowly allowlisted inert documentation/control text;
  - Python/runtime implementation;
  - install/bootstrap/fresh-clone semantics;
  - executable GitHub Actions/control-workflow semantics;
  - unknown/ambiguous fallback.
- Make classification compositional: union all applicable risk classes.
- Do not treat directory placement or filename resemblance alone as proof that a file is inert/platform-specific.
- Keep the `CI:` control surface but deliberately migrate it to unified policy semantics:
  - no selector on automatic push/PR → automatic classification;
  - `CI: auto` → automatic classification;
  - `CI: all` → all six units;
  - `CI: none` → no downstream unit, policy job still runs;
  - explicit comma-separated unit list → exactly those units;
  - `all`, `none`, and `auto` are standalone;
  - duplicates/whitespace may normalize;
  - multiple, unknown, or malformed selectors fail visibly and select all six units.
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
- Do not drop the weekly CodeQL rescan.
- Do not add lower-precision CodeQL query suites, custom queries, path exclusions, model packs, or resource tuning without new evidence.
- Do not add GitHub ruleset configuration in this task; current repository/plan evidence does not justify depending on metadata rulesets.
- Do not add automatic non-main push CI.
- Do not rewrite established Git history.

## Acceptance criteria

- A single small policy job controls launch decisions for all six downstream units.
- The policy job runs on `ubuntu-slim`.
- Push and PR change ranges match documented two-dot/three-dot semantics and fail safe when evidence is unavailable.
- Manual dispatch uses explicit selection rather than inventing an automatic diff.
- Weekly schedule launches only Python and Actions CodeQL units.
- Docs-only changes can produce no downstream runners when confidently classified.
- Python/runtime changes select Linux + Windows + Python CodeQL without fresh-clone validation unless fresh-machine semantics are implicated.
- Install/bootstrap changes select all four blocking sets plus relevant CodeQL.
- Central Actions/policy changes conservatively select all four blocking sets plus both CodeQL units.
- Unknown files or malformed policy metadata select all six units and visibly fail the controller where appropriate.
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
  - path-class unioning;
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
- Verify the weekly schedule remains registered after consolidation.
- Verify ordinary non-main pushes remain quiet.
- Re-read `AGENTS.md`, `.agents/WORKFLOW.md`, and `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md` together after cutover for contradictions.
