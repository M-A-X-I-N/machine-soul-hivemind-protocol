# MSHP-DISC-A-040 — Normalize applied configuration checks

## Description

Make the existing configuration check path rigorously answer only the structural deployment question:

> Is the expected Machine-Soul configuration currently applied at the expected destination, with ownership/state relationships consistent enough to report meaningful deployment state?

This task is intentionally narrower and more implementation-oriented than the installation/effectiveness investigations.

## Requirements

- Review the existing shared configuration check engine and application-specific configuration hooks.
- Define and enforce structural deployment-state semantics such as applied, not applied, wrong target, broken link, unmanaged/conflicting destination, stale ownership/state, and any additional states already justified by the current safety model.
- Ensure `check_config` remains read-only.
- Ensure structural check results do not claim that the application is installed or that the application actually consumes the configuration.
- Preserve meaningful application-specific coupling where structural application state genuinely includes more than a symlink, such as CMD AutoRun integration.
- Keep generic policy in shared runtime code and narrowly scoped application-specific structural checks behind existing extension points.
- Update result details/data, tests, docs, and presentation as needed so callers can reliably interpret structural deployment state.
- Reuse the model/terminology established by `MSHP-DISC-A-010`.

## Constraints / non-goals

- Do not implement installation discovery beyond what is already needed by existing operations.
- Do not implement effective/runtime configuration verification.
- Do not mutate configuration while checking it.
- Do not collapse detailed structural states into a single boolean.
- Do not redesign the overall configuration deployment lifecycle unless a defect prevents consistent structural checking.

## Acceptance criteria

- `check_config` has one unambiguous structural meaning across current applications.
- Applied/not-applied/conflict/broken/wrong-target-style states remain distinguishable where relevant.
- No structural check result implies runtime effectiveness.
- Existing safety invariants and direct/imported wrapper behavior remain intact.
- Tests cover representative normal, broken, wrong-target, conflict, and application-specific structural states.

## Validation

- Run the Python configuration-operation and wrapper/orchestration test suites.
- Run relevant Windows/Linux application integration tests through CI.
- Verify `check_config` does not mutate destinations/state in representative cases.
- Review human and agent documentation for wording that conflates applied configuration with effective configuration.
