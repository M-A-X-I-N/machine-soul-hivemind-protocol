# Discovery semantics

## Decision

Machine-Soul treats installation discovery, structural applied-config checking, and effective-config verification as independent concepts.

- `check_installed` will evolve into a richer installation assessment rather than a boolean executable/package check.
- `check_config` retains the narrow structural deployment meaning.
- effective/runtime configuration verification will use a distinct future atomic operation, `verify_config`.

Discovery/probe code produces observations; shared semantics turn observations plus declaration policy into typed assessments; atomic operations convert assessments to the existing `OperationResult` contract.

Installation mechanism/preference and Machine-Soul ownership are orthogonal dimensions.

Effective-config verification carries explicit evidence strength so application-native/runtime proof is not presented as equivalent to path convention.

The human-facing canonical model is `meta/docs/DISCOVERY_SEMANTICS.md`.
