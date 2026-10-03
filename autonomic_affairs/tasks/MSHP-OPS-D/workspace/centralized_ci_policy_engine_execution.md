# SDD ledger — plan: autonomic_affairs/tasks/MSHP-OPS-D/workspace/centralized_ci_policy_engine_plan.md

Execution method: native/inline on authorized lineage `sera_261003-192400`.

Setup ruling: this harness has no native worktree/terminal checkout attached to the GitHub connector, and the sandbox has no outbound GitHub DNS. Use the isolated Sera branch as the authoritative workspace; materialize focused fetched files into the sandbox for RED→GREEN Python tests and use real GitHub Actions for repository/OS integration validation. Cost if wrong: focused sandbox tests could miss repository-wide coupling until full GitHub validation; the plan therefore retains full-suite and real-Actions gates before integration/completion.

Baseline: `main` and Sera fork from `91e3ad1405ff3b4cb4be9d04d8a48e8fe71fed10`; the prerequisite parity repair's Machine-Soul validation and CodeQL runs completed successfully.

Pre-flight: Task 1 registry/parser/coalescer → Tasks 2/4/5; interfaces agree on stable check IDs and runner-group derivation.
Pre-flight: Task 2 path/event policy → Tasks 3/5; automatic selection feeds scheduled relevance and top-level outputs.
Pre-flight: Task 3 history/reconciliation → Task 5; history yields selected checks through the same policy representation.
Pre-flight: Task 4 reusable workflow inputs/stable step names → Tasks 3/5/7; stable `Check <id>` names are the history identity and selected-check execution contract.
Pre-flight: Task 5 sole entrypoint/callable CodeQL → Task 7; real GitHub validation proves event graph and no duplicate routing.
Pre-flight: Task 6 documentation consumes implemented interfaces only; no conflicting code interface.
Pre-flight: Task 7 consumes all prior outputs; no additional implementation interface.

Task 1: Ruling: add `automatic: bool = False` to `PolicySelection` — `CI: auto` and `CI: none` both otherwise normalize to an empty selected tuple and cannot be distinguished without abusing `source`; cost if wrong: one extra stable policy field carried through later interfaces.

Task 1: complete (commits 7625326..8430ffe, tests: `python -m unittest autonomic_affairs.tests.python.test_ci_validation_selector -v` → 10/10 pass).

Task 2: Ruling: defer the plan's full-repository Python-suite run to Task 7 real GitHub validation — this harness exposes no workflow-dispatch mutation and its sandbox cannot clone GitHub; changing branch-trigger policy just to manufacture the run would contaminate the feature under test. Cost if wrong: repository-wide coupling can surface later at the real cutover instead of this checkpoint.
Task 2: complete (commits 7a02bc6..d8f3fc5, tests: `python -m unittest autonomic_affairs.tests.python.test_ci_validation_selector -v` → 25/25 pass; full-suite gate deferred by ruling above).

Task 3: complete (commits 52dba54..d27ecb2, tests: `python -m unittest autonomic_affairs.tests.python.test_ci_validation_history autonomic_affairs.tests.python.test_ci_validation_selector -v` → 38/38 pass; full-suite gate remains deferred by Task 2 harness ruling).

Task 4: complete (commits c94b4e9..7cc5514, tests: `python -m unittest autonomic_affairs.tests.python.test_ci_workflow_contract autonomic_affairs.tests.python.test_ci_validation_history autonomic_affairs.tests.python.test_ci_validation_selector -v` → 41/41 pass; full-suite gate deferred by Task 2 harness ruling).
Task 5: complete (commits 7cc5514..3d42b4a, tests: `python -m unittest autonomic_affairs.tests.python.test_ci_workflow_contract autonomic_affairs.tests.python.test_ci_validation_selector autonomic_affairs.tests.python.test_ci_validation_history -v` → 45/45 pass; real-Actions/full-suite gate remains Task 7).

Task 6: complete (commits 3d42b4a..42d2db5; validation: branch-specific contradiction scan across `AGENTS.md`, `.agents/WORKFLOW.md`, `.agents/GITHUB_ACTIONS_CONTROL.md`, and `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md` found none of the superseded explicit-only/current-policy statements).

Task 7 probe: docs-only automatic-selection checkpoint; expected policy-only run with no downstream checks.

Task 7 probe: explicit `CI: linux-python` checkpoint; expected one Linux runner with only the linux-python logical check selected.

Task 7 probe: explicit `CI: none` checkpoint; expected successful policy record with no downstream runner provisioning.

Task 7 probe: malformed `CI: linux,banana` checkpoint; expected visible policy failure while fail-safe outputs still select every registered check.

Task 7 probe: native `skip-checks: true` checkpoint; expected no checked-in push workflow run.

Task 7 real-Actions evidence:
- Cutover HEAD `1c950356cc4ec859d902440803f944c073c53663`, run `37160055625`: one top-level Machine-Soul run only; policy used container-backed Ubuntu 24.04 with `actions: read` + `contents: read`, selected all 13 checks from `source=path-classifier`; one Linux job, one Windows job, two fresh-clone jobs, and two CodeQL jobs all succeeded. No independent CodeQL run was created.
- Docs-only HEAD `7698f6de6ab306e54e74057b5569ca093072d2fc`, run `37160154223`: policy selected `none` from `source=path-classifier`; every downstream call was skipped.
- Explicit subset HEAD `f3f2c382df4c8f88bdc9df79010509824229869a`, run `37160211068`: only the Linux runner was provisioned; `Check linux-python` succeeded and the four other Linux checks were skipped; all other runner groups skipped.
- Explicit none HEAD `d3c3fd7cf44068dbe2ac92b9cb87658dd7279e0a`, run `37160253564`: policy selected `none` from `source=commit-trailer`; all downstream calls skipped.
- Invalid selector HEAD `91f4f73415e78715c7be133eb9ecc8f8c4d39a1d`, run `37160279353`: policy failed visibly on unknown group `banana`, emitted all 13 checks, and every downstream blocking/CodeQL job succeeded.
- Native bypass HEAD `784fb3419ab500551a5e08a6933b58f3c306e824`: correctly formatted `skip-checks: true` produced no Actions run.
- Scheduled registration is present as `9 6 * * *`; unit tests cover 24h/168h cadence and real cutover job history proves stable called-workflow step/job identities are visible to the Actions jobs API.
- Manual selected-ref dispatch remains unexercised because the connected GitHub tool exposes inspection/rerun but no workflow-dispatch mutation; the workflow input contract is covered statically. This is a harness limitation, not a substituted test.
