# MSHP-DISC-B-010 — Implement discovery assessment model

## Description

Implement the shared typed value model defined by the DISC-A investigations so discovery backends can return facts and semantic assessments without overloading OperationResult.

This is the common dependency for richer installation discovery and effective-configuration verification.

## Requirements

- Add immutable shared discovery value types under the Machine-Soul Python model layer.
- Represent observation kind/source, structured evidence data, and evidence strength explicitly.
- Implement the effective-verification evidence ordering established by DISCOVERY_SEMANTICS.md: runtime, application, resolution, convention, none.
- Implement installation-presence semantics for present, absent, ambiguous, and unknown.
- Implement independent tri/explicit-state dimensions where needed for facts such as preferred-strategy match/manageability rather than encoding them into combinatorial result codes.
- Implement an InstallationCandidate capable of carrying identity, version, paths, scope, registration kind, acquisition-channel evidence, preferred-strategy compatibility, Machine-Soul ownership/provenance relation, uninstall identity, and supporting observations when available.
- Implement an InstallationAssessment carrying overall presence, all candidates, optional preferred candidate/reference, Machine-Soul state relationship, and observations/errors needed to explain unknown/ambiguous outcomes.
- Implement effective-configuration observation/assessment types carrying conclusion (effective, not_effective, indeterminate), strongest evidence level, and all supporting observations.
- Provide deterministic JSON-serializable representations suitable for OperationResult.data and machine output.
- Validate enum/value invariants and reject impossible malformed assessment objects early.
- Update human/agent architecture docs only where concrete implementation names materially differ from the earlier conceptual wording.

## Constraints / non-goals

- Do not add platform package-manager/process probes in this task.
- Do not add verify_config to the Operation enum yet.
- Do not change ResultStatus or turn OperationResult into the discovery object itself.
- Do not encode every combination of installation facts as a new enum value.
- Do not implement installation takeover.

## Acceptance criteria

- Installation and verification assessments are ordinary typed Python objects independent of CLI/presentation.
- Independent dimensions such as preferred match and Machine-Soul ownership remain independent.
- All assessment forms serialize losslessly enough for OperationResult.data and tests.
- Unknown and ambiguous states can retain partial evidence/candidates rather than discarding them.
- Existing operations/tests remain green.

## Validation

- Unit-test construction, invariants, immutability, equality, serialization, and malformed input.
- Walk the representative DISC-A scenarios from DISCOVERY_SEMANTICS.md using the concrete value types.
- Run the Python model/result test suite and full CI.
