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
