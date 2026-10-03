# MSHP-OPS-D-010 — Investigate centralized CI policy engine

## Description

Investigate replacing today's simple explicit dispatcher plus independent CodeQL trigger with one conservative control-plane decision job that can choose downstream validation based on explicit overrides plus event/diff evidence.

## Requirements

- Treat one small control runner as acceptable; the objective is avoiding unnecessary downstream runner provisioning, not pretending the control logic is runnerless.
- Map how to compute reliable changed-file evidence for push/PR/manual events and how merge ranges/multi-commit pushes affect classification.
- Design explicit override semantics (`CI:` or successor) where overrides remain validated and authoritative.
- Investigate conservative automatic classifications such as docs-only, Python/runtime changes, Actions-workflow changes, bootstrap/install changes, and uncertain fallback-to-all.
- Investigate integrating CodeQL Python/Actions as separately selectable downstream analyses under the same control decision while preserving deferred-CI semantics and periodic security rescanning.
- Investigate commit-message/control metadata validation as part of the selector and the role of GitHub rulesets for hard grammar constraints.
- Compare runner options suitable for the small control plane, including current slim/container choices where supported.
- Produce an evidence-based target architecture and only then taskify implementation.

## Constraints / non-goals

- Do not implement the new policy engine in this task.
- Do not infer safety from paths alone; classification must fail safe when uncertain.
- Do not optimize solely for billed minutes.
- Do not discard explicit overrides or periodic CodeQL value without evidence.

## Acceptance criteria

- A concrete event/diff/override decision model exists.
- Downstream blocking and CodeQL units are mapped.
- Fail-safe/default behavior is explicit.
- The investigation says which current OPS-A/OPS-B policies must be superseded rather than silently contradicting them.
- Only justified follow-up tasks are created.

## Validation

- Use current official GitHub Actions/CodeQL/ruleset documentation and repository experiments where useful.
- Measure/inspect current workflow behavior before recommending cutover.
