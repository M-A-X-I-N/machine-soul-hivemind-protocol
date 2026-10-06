# MSHP-OPS-A-010 — Codify agent-lineage and selective-CI policy

## Description

Codify the repository operating model for recoverable agent lineages, owned working-branch namespaces, explicit CI selection, and deferred validation before changing GitHub Actions behavior.

## Requirements

- Define an agent-lineage identifier as `{name}_YYMMDD-HHmmss`.
- Require `name` to be exactly four lowercase ASCII letters forming a short female, neutral, or fantasy-style human-readable name; do not maintain a canonical name registry. Prefer an initial not already in active/recent use when practical.
- Define the timestamp as UTC lineage-creation time with second precision and keep it stable for the life of the lineage.
- Define `agent/{identifier}/*` as the lineage-owned branch namespace and `agent/{identifier}/main` as its canonical working branch.
- Allow a lineage to create any additional valid branches under its namespace without task/feature-branch ceremony.
- Define recovery/takeover semantics: a replacement chat/agent may adopt an existing lineage when continuing the same work; a transport/session reset does not itself require a new identifier.
- Make normal substantive development prefer the lineage namespace while explicitly allowing direct `main` work when that is the natural/simpler repository operation.
- Define CI policy around validation value rather than minimizing usage:
  - pushes to `main` run all blocking validation by default;
  - a main integration event may explicitly select a registered subset or `none` when full validation would be wasteful;
  - non-main pushes do not automatically run the normal validation suite;
  - CI may be explicitly invoked against an agent branch/ref whenever intermediate validation is useful;
  - do not infer CI selection from changed paths.
- Define a durable explicit selector contract using a `CI:` commit trailer for main-push overrides: `CI: all`, `CI: none`, or a comma-separated list of registered validation-set names. The pushed main tip controls the integration event when a push contains multiple commits.
- Define `AWAITING_DEFERRED_CI` as a lifecycle state for work whose implementation and advancement-blocking validation are complete while explicitly deferred repository analysis remains pending.
- Define advancement/completion semantics for deferred CI:
  - advancement-blocking CI must pass before leaving active implementation;
  - a task may enter `AWAITING_DEFERRED_CI` and later work may begin;
  - a task cannot become `COMPLETE` until its required deferred checks pass;
  - later tasks must not be marked `COMPLETE` while an earlier task in the same ordered workstream remains unresolved in `AWAITING_DEFERRED_CI`;
  - substantive deferred-analysis failures reopen/block the originating work, while infrastructure-only failures are retried/investigated separately.
- Document that `FROZEN` represents an intentional pause/priority hold rather than a dependency or technical blocker.
- Update the authoritative task-state contract and concise agent workflow guidance consistently.
- Establish the executing lineage's first canonical `agent/{identifier}/main` branch after the policy checkpoint so subsequent OPS-A implementation can use the new model.

## Constraints / non-goals

- Do not implement the Actions dispatcher or reusable validation workflows in this task.
- Do not add path-based CI routing.
- Do not maintain a central list of allowed agent names.
- Do not require every repository edit to occur on an agent branch.
- Do not tie agent-lineage identity to a specific ChatGPT transport/session identifier that is not repository-controlled.

## Acceptance criteria

- Human-facing and agent-facing policy agree on identifier format, branch ownership, recovery, main/non-main CI defaults, explicit selectors, and deferred-CI semantics.
- `AWAITING_DEFERRED_CI` is a valid documented task lifecycle state.
- The frozen DEV-B checkpoint is described as intentionally paused pending this block.
- A canonical branch exists for the executing agent lineage and is ready for subsequent OPS-A work.

## Validation

- Reread all modified policy/task-contract files for contradiction.
- Verify documented branch names are valid Git refs and use the exact canonical shapes.
- Verify no path-based CI selection is introduced.
- Inspect the created agent namespace/ref and confirm it starts from the intended main checkpoint.
