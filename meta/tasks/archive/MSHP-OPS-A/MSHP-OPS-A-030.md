# MSHP-OPS-A-030 — Implement explicit CI dispatcher and selectors

## Description

Implement the explicit CI control plane: conservative automatic validation on main, quiet agent branches by default, and deliberate validation-set selection when full CI would be wasteful or intermediate branch validation is useful.

## Requirements

- Add a thin dispatcher/orchestration workflow using the reusable validation sets from MSHP-OPS-A-020.
- On pushes to `main`:
  - when the pushed tip commit has no `CI:` trailer, dispatch all registered blocking validation sets;
  - `CI: all` explicitly dispatches all registered blocking validation sets;
  - `CI: none` intentionally dispatches no normal blocking validation sets;
  - `CI: set-a,set-b` (with documented whitespace handling) dispatches exactly the named registered sets.
- Treat the pushed `main` tip's selector as controlling the whole integration event when multiple commits arrive in one push.
- Parse selectors strictly. Unknown/malformed selectors must never silently reduce validation; fail safe by ensuring full validation still runs and surface a selector/control-plane failure that requires correction.
- Do not automatically run the normal validation suite for pushes to non-main branches, including `agent/**`.
- Expose `workflow_dispatch` so a human/agent can explicitly run all or selected registered validation sets against a chosen ref/agent branch.
- Ensure manual branch validation can select useful subsets without merging/pushing to main.
- Remove/disable superseded automatic triggers so the dispatcher does not duplicate the same validation work.
- Keep selector logic testable and documented; prefer a small deterministic parser/control step over duplicated YAML conditions.
- Keep GitHub-managed deferred analysis separate from blocking validation-set dispatch unless GitHub requires otherwise.
- Do not introduce path filters or changed-file inference.

## Constraints / non-goals

- Do not optimize for minimum CI usage at the cost of useful validation.
- Do not require a feature branch per task.
- Do not make manual branch validation mandatory after every commit.
- Do not silently treat malformed `CI:` directives as `none` or a smaller subset.
- Do not redesign the tests themselves beyond what the dispatcher/reuse boundary requires.

## Acceptance criteria

- Main defaults to full blocking validation with no selector.
- Main can explicitly request all, none, or an exact named subset.
- Non-main pushes are quiet by default.
- Explicit manual dispatch can validate a selected agent ref with all or a selected subset.
- Invalid selectors are safe and visible.
- No path-based routing exists.
- One integration event does not spawn duplicate copies of the same validation sets.

## Validation

- Add deterministic tests/checks for selector parsing, whitespace, duplicates, unknown names, missing selectors, `all`, and `none`.
- Exercise manual dispatch against an agent branch.
- Exercise main default behavior and at least one explicit selector behavior.
- Inspect actual workflow jobs/runs to verify only the intended sets were provisioned.
