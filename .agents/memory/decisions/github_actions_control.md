# GitHub Actions control-plane observations

> **Historical evidence:** the OPS-A dispatcher behavior below was verified and remains useful test evidence, but its routing policy is superseded by MSHP-OPS-D. Current policy lives in `autonomic_affairs/docs/AGENT_LINEAGES_AND_CI.md`, `.agents/baseline/WORKFLOW.md`, and `.agents/local/CI.md`.

## Current control-plane model

- One top-level Machine-Soul policy workflow owns push-to-main, PR-to-main, manual, and `9 6 * * *` scheduled entry.
- Changed paths are conservative automatic evidence; explicit valid `CI:` selection is authoritative; uncertainty fails safe to all registered checks.
- Selection is check-level, then compatible checks are coalesced onto shared runner jobs.
- CodeQL Python/Actions are selected by the same policy engine but retain deferred lifecycle semantics.
- Scheduled reconciliation derives coverage from repository history plus GitHub Actions run/job/step history; no separate persistent CI-state database is authoritative.


Verified while implementing MSHP-OPS-A in lineage `lyra_260928-230718`.

## Superseded OPS-A validation sets and dispatcher

Registered blocking validation sets are `linux`, `windows`, `fresh-linux`, and `fresh-windows`.

The checked-in dispatcher uses one small selector job, then conditionally calls reusable workflows. Ordinary pushes to agent branches do not match the normal push trigger. Main pushes default to all registered sets unless the tip commit contains an explicit `CI:` selector. Native `skip-checks: true` bypasses the checked-in push workflow entirely.

## Observed runs

- Refactor checkpoint `f870856`: an ordinary agent-branch push produced no workflow run; moving the same commit onto `main` launched all four extracted reusable validation sets successfully.
- Dispatcher checkpoint `02417a5`: an ordinary agent-branch push produced no workflow run; main integration selected all four sets through `source=main-default`, and all four passed.
- Subset checkpoint `97b1d4d`: main integration read `CI: linux`, ran only `linux`, and marked `windows`, `fresh-linux`, and `fresh-windows` skipped; the selected Linux set passed.
- None checkpoint `24b32d7`: main integration read `CI: none`; the selector passed and all four validation-set jobs were skipped without provisioning their runners.
- Fail-safe checkpoint `aecaace`: main integration read the invalid `CI: linux,banana`; the selector failed visibly, selected all four registered sets, and all four validation sets passed.
- Manual-dispatch run `36497684524`: a one-off GitHub-token probe created a real `workflow_dispatch` event against `agent/lyra_260928-230718/main` with `sets=linux`; the selector reported `source=manual-dispatch`, Linux passed, and the other three sets were skipped.
- Dynamic GitHub-managed CodeQL/default code scanning is independent of the checked-in skip mechanism: it still started on a main commit whose message used `[skip ci]`. Treat its trigger/control semantics separately from the repository dispatcher.

## Tool-surface limitation

The currently available GitHub connector can inspect Actions runs/jobs/logs and rerun existing jobs, but it does not directly expose creation of a `workflow_dispatch` event. MSHP-OPS-A verified the event indirectly with a temporary GitHub Actions probe using the repository `GITHUB_TOKEN`; the probe workflow was then removed from its branch.

Do not work around connector limitations by weakening branch trigger policy. The old prohibition on changed-path routing is superseded: current OPS-D policy deliberately uses changed paths as conservative evidence with fail-safe fallback.
