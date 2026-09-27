# Orchestration boundary

V2-56 fixes the interactive-manager contract.

The manager:

- discovers/selects atomic operations;
- calls the same wrapper `run(...)` interfaces used by direct execution;
- propagates shared operation context;
- aggregates common `OperationResult` objects;
- owns interaction/presentation/composition only.

It must not implement application/platform/config/install/state/native-primitive policy.

Prefer in-process imports for Python wrappers. Spawn only for a real process/isolation/external/native boundary. Any spawned result is normalized before orchestration sees it.

Mixed outcomes stay individually visible; never flatten partial-change/error information into a single boolean.

If a new application requires application-specific orchestrator logic, the lower abstractions are missing a capability.
