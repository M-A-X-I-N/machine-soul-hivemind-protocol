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
