# MSHP-LAYOUT-A-030 — Shorten the Machine-Soul functional trees

## Description

Rename the two core Machine-Soul domain trees while preserving their architectural distinction:

- `annexation_procedures/` → `annexation/`
- `assimilation_directives/` → `assimilation/`

## Requirements

- Move all operational/runtime/application machinery from `annexation_procedures/` to `annexation/`.
- Move canonical tracked desired configuration/behavior from `assimilation_directives/` to `assimilation/`.
- Update Python package imports, wrappers, module references, tests, scripts, documentation, configuration resolution, CI path rules, and examples.
- Preserve the semantic distinction: annexation is operational machinery; assimilation is canonical desired behavior/configuration.
- Preserve application pairing and existing configuration resolution semantics.

## Constraints / non-goals

- Do not merge annexation and assimilation into one tree.
- Do not redesign package/module architecture merely because imports are being renamed.
- Do not change configuration precedence, ownership semantics, or installation behavior unless a path-only compatibility fix requires it.
- Do not rename `.machine_soul_root`.

## Acceptance criteria

- Live code imports/runs through `annexation`.
- Canonical configuration resolves from `assimilation`.
- No live runtime/test/CI path depends on the two old directory names.
- Existing operation/configuration behavior remains unchanged apart from repository paths.

## Validation

- Run Python tests covering discovery, configuration, operations, and application declarations.
- Run relevant matrix/session tests where path assumptions exist.
- Search live source/tests/workflows/docs for stale executable references to the old names.
- Verify representative Apply/Check source resolution still points into `assimilation/`.
