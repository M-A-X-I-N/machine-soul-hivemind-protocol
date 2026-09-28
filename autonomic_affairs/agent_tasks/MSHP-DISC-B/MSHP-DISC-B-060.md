# MSHP-DISC-B-060 — Establish verify_config operation

## Description

Implement the distinct effective-configuration operation and shared verification engine defined by DISC-A, without yet adding application-specific verification strategies.

## Requirements

- Add VERIFY_CONFIG / verify_config to the Operation model and capability contract.
- Add uniform verify_config.py atomic wrappers for current applications using the same importable/executable wrapper pattern as other operations.
- Extend PlatformDeclaration with explicit configuration-verification plan/strategy declarations independent from structural configuration destination strategy.
- Add a shared verification engine that executes declared reusable verification strategies, collects observations, builds the concrete verification assessment from MSHP-DISC-B-010, and maps it to OperationResult.
- Preserve semantic conclusions effective, not_effective, and indeterminate separately from evidence strength.
- Preserve unsupported/not-implemented operation capability separately from an indeterminate supported verification result.
- Carry all useful serialized observations/evidence in OperationResult.data.
- Do not gate verification solely on check_config success; a verifier should report what the application actually resolves/consumes.
- Update dispatcher, wrapper discovery, capability/docs, manager list output, and contract tests for the new operation.
- Initially leave application verification capability NOT_IMPLEMENTED where later tasks have not yet supplied a strategy.
- Use DISCOVERY_SEMANTICS.md and CONFIGURATION_VERIFICATION.md as the durable contract.

## Constraints / non-goals

- Do not implement shell tracing in this task.
- Do not implement OMP/Contour/CMD/Terminal-specific probes in this task.
- Do not alter structural check_config semantics.
- Do not mutate configuration to obtain verification evidence.

## Acceptance criteria

- verify_config exists as a first-class atomic operation across direct, imported, dispatcher, and wrapper-discovery surfaces.
- Supported verification strategies can return typed assessments and stable OperationResults.
- Unsupported/not implemented and indeterminate are not conflated.
- Existing six operation behaviors remain unchanged apart from discovery count/tests being intentionally updated for the seventh operation.

## Validation

- Unit-test operation/capability dispatch, assessment-to-result mapping, no-strategy/not-implemented, effective/not_effective/indeterminate, JSON output, and direct/imported wrapper behavior.
- Update wrapper/orchestrator parity expectations.
- Run full CI.
