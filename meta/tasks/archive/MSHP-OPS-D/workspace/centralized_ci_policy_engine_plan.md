# Centralized CI Policy Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace split CI routing with one conservative selector/policy entry point that chooses relevant checks, coalesces compatible checks onto shared runners, and reconciles missing coverage on a daily 06:09 UTC schedule.

**Architecture:** Keep `autonomic_affairs/ci_validation_selector.py` as the policy core and CLI, with pure deterministic selection logic separated from GitHub-history I/O. The top-level Machine-Soul workflow becomes the sole push/PR/manual/schedule entry point; downstream Linux, Windows, fresh-clone, and CodeQL workflows become callable execution groups. Selection happens at check granularity, while runner provisioning happens only after selected checks are coalesced by compatible environment.

**Tech Stack:** Python 3 standard library, Git CLI, GitHub Actions reusable workflows, GitHub Actions REST API via `GITHUB_TOKEN`, CodeQL Actions v4.

**Spec:** `autonomic_affairs/tasks/MSHP-OPS-D/MSHP-OPS-D-020.md`; supporting synthesis: `autonomic_affairs/tasks/MSHP-OPS-D/workspace/centralized_ci_policy_engine.md`.

## Global Constraints

- `.github/workflows/machine_soul_validation.yml` is the sole CI event entry point for push-to-main, PR-to-main, manual dispatch, and schedule.
- Ordinary non-main pushes stay quiet.
- Scheduled reconciliation is `9 6 * * *` (06:09 UTC).
- The policy job runs on `ubuntu-slim`.
- Changed paths are conservative evidence, never authority; missing/ambiguous evidence selects the complete registered check set.
- Check relevance and runner provisioning are separate: selected compatible checks share one runner job.
- Valid explicit `CI:` overrides are authoritative; malformed control metadata visibly fails safe to all checks.
- Native correctly formatted `skip-checks: true` remains the hard GitHub-level event bypass.
- CodeQL stays deferred, uses `actions` + `python`, `build-mode: none`, the default query suite, stable language categories, and least-privilege upload permissions.
- Scheduled CodeQL requires exact-current-HEAD success: 24-hour cadence while HEAD age is under 168 hours, then 168-hour cadence.
- Scheduled ordinary-check coverage may carry forward from an older successful SHA only when no check-relevant path changed afterward.
- No new third-party Python dependency and no persistent CI-state database.
- Current direct-main prerequisite repair `91e3ad1405ff3b4cb4be9d04d8a48e8fe71fed10` restored a green baseline before this plan.

## Review Focus

1. **Historical step identity:** called reusable-workflow jobs and steps must retain stable machine-recognizable names; a renamed check must not silently inherit another check's success.
2. **Skipped versus successful:** a skipped conditional step must never count as successful coverage for that check.
3. **History gaps/retention:** missing pages, unreachable old SHAs, API failure, or no recognized historical check result must select the affected check rather than assume coverage.
4. **Range ambiguity:** forced pushes, all-zero/missing push base, missing PR merge base, and shallow/missing Git objects must select all checks.
5. **Self-modifying control plane:** any selector/workflow/relevance-registry change must conservatively select the complete blocking check set plus both CodeQL checks.

---

### Task 1: Define check registry, selector grammar, and runner coalescing

**Files:**
- Modify: `autonomic_affairs/ci_validation_selector.py`
- Modify: `autonomic_affairs/tests/python/test_ci_validation_selector.py`

**Interfaces:**
- Produces: `REGISTERED_CHECKS: tuple[str, ...]`
- Produces: `GROUP_ALIASES: dict[str, tuple[str, ...]]`
- Produces: `PolicySelection(selected: tuple[str, ...], valid: bool, source: str, error: str | None)`
- Produces: `parse_selector(selector: str | None, *, source: str, default_auto: bool = False) -> PolicySelection`
- Produces: `runner_groups_for_checks(checks: Iterable[str]) -> dict[str, tuple[str, ...]]`

Initial stable check IDs:

- `linux-python`
- `linux-applications`
- `linux-install`
- `linux-session`
- `linux-matrix`
- `windows-python`
- `windows-applications`
- `windows-posix`
- `windows-install`
- `fresh-linux`
- `fresh-windows`
- `codeql-python`
- `codeql-actions`

Compatibility/convenience aliases:

- `linux` expands all `linux-*` checks.
- `windows` expands all `windows-*` checks.
- `fresh-linux` / `fresh-windows` remain exact checks.
- `all` expands every registered check.
- `none` expands none.
- `auto` is standalone and delegates to automatic classification.

- [ ] **Step 1: Add failing selector tests**

Add tests for exact check IDs, `linux`/`windows` alias expansion, mixed group + exact selections, normalized duplicate ordering, `auto`, `all`, `none`, forbidden mixing of standalone tokens, and malformed/unknown fail-safe to every registered check.

- [ ] **Step 2: Run selector tests and confirm RED**

Run: `python -m unittest autonomic_affairs.tests.python.test_ci_validation_selector -v`

Expected: failures because check registry, aliases, and `PolicySelection` do not exist yet.

- [ ] **Step 3: Implement the registry/parser/coalescer**

Keep parsing deterministic and ordered by `REGISTERED_CHECKS`. Runner groups are `linux`, `windows`, `fresh-linux`, `fresh-windows`, `codeql-python`, and `codeql-actions`; each group receives only its selected check IDs.

- [ ] **Step 4: Run selector tests and confirm GREEN**

Run the Task 1 test command; expected all tests pass.

- [ ] **Step 5: Commit**

Commit summary: `[Feature][CI] Add check-level policy registry`

### Task 2: Add conservative path classification and event-range resolution

**Files:**
- Modify: `autonomic_affairs/ci_validation_selector.py`
- Modify: `autonomic_affairs/tests/python/test_ci_validation_selector.py`

**Interfaces:**
- Produces: `checks_for_paths(paths: Iterable[str]) -> PolicySelection`
- Produces: `git_changed_paths(base: str, head: str, *, three_dot: bool = False) -> tuple[str, ...]`
- Produces: `validate_commit_summary(summary: str) -> str | None`
- Produces: `resolve_automatic_event(...) -> PolicySelection`

Classification contract:

- Central CI/control files (`.github/workflows/**`, selector/history modules, their tests) select all registered checks.
- Narrowly allowlisted inert Markdown/text under docs/task/agent-memory surfaces selects no downstream check unless a known control/test surface explicitly consumes it.
- Python source changes always select `codeql-python`; `annexation_procedures/**.py` selects all non-fresh Linux/Windows integration checks because those shells/wrappers consume the shared runtime, while install/bootstrap surfaces additionally select both fresh-clone checks.
- Actions workflow changes select `codeql-actions`; validation/control workflow changes select all blocking checks plus both CodeQL checks.
- Install/bootstrap/fresh-machine surfaces select their relevant install/fresh checks plus language analysis.
- Unknown/unclassified paths select all checks.
- Deleted/renamed paths use both old/new names when Git supplies them.

Event contract:

- push: two-dot event `before` → `after`; forced/missing/all-zero base fails safe to all;
- PR: three-dot base → head; missing merge base fails safe to all;
- manual: explicit selection only, default `all`;
- schedule: delegated to Task 3 reconciliation.

- [ ] **Step 1: Add failing classification and range tests**

Cover inert docs, ordinary Python, install/bootstrap, Actions/control, unknown fallback, path unions, multi-commit push, PR merge-base graph, forced push, missing object, and renamed path behavior. Use temporary Git repositories for real two-dot/three-dot behavior rather than mocking Git.

- [ ] **Step 2: Add failing commit-control metadata tests**

Allow approved `[Kind][Scope] Summary` / `[Kind] Summary` forms and reject malformed summaries; verify multiple/invalid `CI:` lines fail safe.

- [ ] **Step 3: Run selector tests and confirm RED**

Expected: failures for missing classification/range/metadata functions.

- [ ] **Step 4: Implement classification, Git range resolution, and metadata validation**

Use `subprocess.run(..., check=True)` for Git and convert any inability to prove the intended range into fail-safe selection rather than partial evidence.

- [ ] **Step 5: Run selector tests and full Python suite**

Run:
- `python -m unittest autonomic_affairs.tests.python.test_ci_validation_selector -v`
- `python -m unittest discover -s autonomic_affairs/tests/python -p 'test_*.py'`

Expected: both green.

- [ ] **Step 6: Commit**

Commit summary: `[Feature][CI] Classify event changes conservatively`

### Task 3: Add GitHub history and scheduled coverage reconciliation

**Files:**
- Create: `autonomic_affairs/ci_validation_history.py`
- Create: `autonomic_affairs/tests/python/test_ci_validation_history.py`
- Modify: `autonomic_affairs/ci_validation_selector.py`
- Modify: `autonomic_affairs/tests/python/test_ci_validation_selector.py`

**Interfaces:**
- `GitHubActionsHistory(repository: str, token: str, current_run_id: int)`
- `GitHubActionsHistory.recent_runs() -> tuple[dict, ...]`
- `GitHubActionsHistory.jobs_for_run(run_id: int) -> tuple[dict, ...]`
- `successful_check_executions(history, *, current_run_id: int) -> dict[str, tuple[str, datetime]]`
- `reconcile_scheduled_checks(..., now: datetime) -> PolicySelection`

History rules:

- Read Actions history with stdlib HTTP and `Authorization: Bearer $GITHUB_TOKEN`.
- Follow pagination far enough to establish usable coverage; inability to establish it is uncovered, not covered.
- Ignore current run.
- Recognize only stable `Check <check-id>` step names (or exact CodeQL job identities defined in Task 5).
- Count only `success`; `skipped`, `failure`, `cancelled`, and absent steps provide no coverage.
- Empirically verified current GitHub behavior: jobs/steps from called reusable workflows are visible through the parent run's jobs API.

Scheduled ordinary-check rule:

- Current-HEAD success covers.
- Older success covers only if diff old SHA → current HEAD has no path relevant to that check.
- Incomparable/unreachable SHA or diff failure means due.

Scheduled CodeQL rule, independently per language:

- no success on exact current HEAD → due now;
- HEAD age < 168h → due when last exact-HEAD success age >= 24h;
- HEAD age >= 168h → due when last exact-HEAD success age >= 168h.

- [ ] **Step 1: Write failing history parsing tests**

Fixtures cover called-workflow job names, stable check-step names, skipped steps, failed jobs, current-run exclusion, multiple historical runs, and no usable history.

- [ ] **Step 2: Write failing scheduled reconciliation tests**

Cover unrelated-change carry-forward, relevant-change invalidation, unreachable old SHA fallback, CodeQL exact-HEAD requirement, 24h boundary, 168h HEAD-age transition, and independent Python/Actions CodeQL coverage.

- [ ] **Step 3: Run new tests and confirm RED**

Run: `python -m unittest autonomic_affairs.tests.python.test_ci_validation_history autonomic_affairs.tests.python.test_ci_validation_selector -v`

- [ ] **Step 4: Implement history client and reconciliation**

Keep HTTP/I/O in `ci_validation_history.py`; keep policy decisions in the selector module. No on-disk state.

- [ ] **Step 5: Run focused tests and full Python suite**

Expected green.

- [ ] **Step 6: Commit**

Commit summary: `[Feature][CI] Reconcile scheduled check coverage`

### Task 4: Make blocking validation workflows check-selectable without multiplying runners

**Files:**
- Modify: `.github/workflows/machine_soul_validation_linux.yml`
- Modify: `.github/workflows/machine_soul_validation_windows.yml`
- Modify: `.github/workflows/machine_soul_validation_fresh_linux.yml`
- Modify: `.github/workflows/machine_soul_validation_fresh_windows.yml`
- Modify: `autonomic_affairs/tests/python/test_ci_validation_selector.py` or add a focused workflow-contract test if clearer

**Interfaces:**
- Each reusable workflow accepts a string input `checks_json`.
- Each logical check step uses stable name `Check <check-id>`.
- Linux/Windows workflow jobs run once and condition individual check steps with `contains(fromJSON(inputs.checks_json), '<check-id>')`.
- Python runtime smoke/setup may run whenever that OS runner is provisioned but is not itself historical check coverage.
- Fresh workflows expose one stable check each.
- Upgrade touched checkout actions to `actions/checkout@v7`.

- [ ] **Step 1: Add failing workflow-contract tests**

Parse workflow text/YAML conservatively enough to assert each registered blocking check has exactly one stable `Check <id>` step and that Linux/Windows checks share one job per OS.

- [ ] **Step 2: Run workflow-contract tests and confirm RED**

- [ ] **Step 3: Add `workflow_call.inputs.checks_json` and conditional stable check steps**

Do not split current Linux/Windows steps into separate jobs. Preserve cleanup/scratch isolation already implemented by the test scripts.

- [ ] **Step 4: Run Python suite**

Expected green.

- [ ] **Step 5: Commit**

Commit summary: `[CI][Validation] Share runners across selected checks`

### Task 5: Centralize all event routing and make CodeQL callable

**Files:**
- Modify: `.github/workflows/machine_soul_validation.yml`
- Modify: `.github/workflows/codeql.yml`
- Modify: `autonomic_affairs/ci_validation_selector.py`
- Modify: workflow-contract tests from Task 4

**Interfaces:**
- Top-level triggers: push `main`, PR targeting `main`, `workflow_dispatch`, schedule `9 6 * * *`.
- Policy job: `runs-on: ubuntu-slim`, `permissions: {contents: read, actions: read}`, checkout `fetch-depth: 0`.
- Policy outputs: per-runner selected-check JSON + booleans for runner provisioning + `codeql_python` / `codeql_actions` + validity/selection diagnostic outputs.
- Manual input retains `sets` for compatibility and accepts explicit checks/groups plus `all`/`none`; `auto` is rejected fail-safe because manual dispatch has no event diff to classify.
- `codeql.yml` becomes `workflow_call` only with required `language` input constrained by caller to `python` or `actions`.
- Caller CodeQL jobs grant `contents: read` and `security-events: write`; policy job never receives `security-events: write`.
- Invalid policy may fail the policy job while `always()` downstream conditions still launch the fail-safe check set from already-written outputs.

- [ ] **Step 1: Add failing top-level workflow tests**

Assert one event entry point, exact cron `9 6 * * *`, `ubuntu-slim`, full-history checkout, read-only policy permissions, no event triggers in `codeql.yml`, and six downstream runner groups/calls only when outputs select them.

- [ ] **Step 2: Run workflow tests and confirm RED**

- [ ] **Step 3: Refactor CodeQL to one-language reusable workflow**

Preserve default queries, `build-mode: none`, and category `/language:<language>`.

- [ ] **Step 4: Refactor top-level workflow around policy outputs**

Pass per-OS selected-check arrays to reusable workflows; call CodeQL independently per selected language.

- [ ] **Step 5: Run full Python suite**

Expected green.

- [ ] **Step 6: Commit**

Commit summary: `[CI][Control] Centralize repository CI entrypoint`

### Task 6: Supersede old CI policy documentation

**Files:**
- Modify: `AGENTS.md`
- Modify: `.agents/WORKFLOW.md`
- Modify: `.agents/GITHUB_ACTIONS_CONTROL.md` if present
- Modify: `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md`
- Modify: `autonomic_affairs/tasks/MSHP-OPS-D/workspace/centralized_ci_policy_engine.md` only where implementation discovered a necessary correction

**Interfaces:** Documentation must describe the implemented check IDs/groups, event/range semantics, 06:09 UTC reconciliation, adaptive CodeQL cadence, check-vs-runner distinction, fail-safe behavior, and `CI:`/native skip relationship.

- [ ] **Step 1: Replace superseded OPS-A/OPS-B live policy statements**

In particular remove live claims that main always defaults all, changed paths never influence selection, CodeQL routes separately, or `CI:` cannot select CodeQL.

- [ ] **Step 2: Preserve historical evidence as historical**

Do not rewrite old experiment results in `.agents/GITHUB_ACTIONS_CONTROL.md`; clearly mark the old dispatcher behavior superseded and add the new current model.

- [ ] **Step 3: Search for contradictory live guidance**

Search tracked policy/startup surfaces for:
- `do not infer CI selection from changed paths`
- `main.*default.*all`
- `CI:.*only.*blocking`
- `CodeQL.*separate.*dispatcher`
- old weekly-only schedule wording

Expected: no authoritative current-policy contradiction remains.

- [ ] **Step 4: Commit**

Commit summary: `[Documentation][CI] Document centralized check policy`

### Task 7: Validate cutover on real GitHub Actions and complete D-020

**Files:**
- Modify only if validation finds a defect.
- Final bookkeeping: `autonomic_affairs/tasks.md`.

- [ ] **Step 1: Run the complete local/static Python suite on Sera**

Run: `python -m unittest discover -s autonomic_affairs/tests/python -p 'test_*.py'`

Expected: green.

- [ ] **Step 2: Verify Sera contains no unrelated divergence from current main**

Compare `main...` Sera and reconcile if main moved unexpectedly.

- [ ] **Step 3: Integrate the implementation checkpoint to main without a manual override**

The central-control diff itself must classify conservatively and provision the complete blocking check set plus both CodeQL checks.

- [ ] **Step 4: Inspect the actual top-level run**

Verify:
- policy job uses `ubuntu-slim`;
- all selected logical checks appear as stable steps;
- compatible checks share Linux/Windows jobs rather than separate VMs;
- both fresh checks run;
- CodeQL Python and Actions run once each;
- no legacy independent CodeQL run is created for the same push.

- [ ] **Step 5: Exercise selective behavior on main with safe evidence-backed checkpoints**

Use small representative commits/checkpoints to prove at least:
- inert docs-only → policy only / no downstream runner when no control-consumed doc changed;
- valid explicit subset → only named checks/groups;
- `CI: none` → policy only;
- malformed selector → policy failure + complete fail-safe downstream checks.

Do not manufacture destructive product changes solely for CI experiments; use task/workspace/doc fixtures or reversible CI test fixtures.

- [ ] **Step 6: Verify scheduled/manual registration**

Confirm GitHub registers `workflow_dispatch` and cron `9 6 * * *`. If the available connector exposes workflow dispatch, run selected-ref manual validation; otherwise document that limitation exactly rather than manufacturing a substitute.

- [ ] **Step 7: Validate scheduled reconciliation logic against real run-history shape**

Use the successful integration run's jobs API as the historical fixture source and confirm the parser recognizes stable check steps and CodeQL identities. Do not wait for 06:09 UTC merely to prove deterministic age logic already covered by tests.

- [ ] **Step 8: Handle deferred CodeQL lifecycle**

If blocking checks finish before selected CodeQL, set D-020 to `AWAITING_DEFERRED_CI`; mark `COMPLETE` only after required CodeQL succeeds.

- [ ] **Step 9: Final policy/task consistency pass**

Re-read `AGENTS.md`, `.agents/WORKFLOW.md`, `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md`, task spec, and live workflow together.

- [ ] **Step 10: Complete bookkeeping**

On success: set D-020 `COMPLETE`, remove Sera's Active claim, and leave Dispatch consistent with whatever work is actually authorized next.

- [ ] **Step 11: Commit final bookkeeping**

Commit summary: `[Documentation][Tasks] Complete centralized CI policy implementation`
