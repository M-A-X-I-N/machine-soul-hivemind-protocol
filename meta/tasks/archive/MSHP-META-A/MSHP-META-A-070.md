# MSHP-META-A-070 — Rehome assimilation runtime

## Description

Correct the repository taxonomy by relocating the core Machine-Soul Python deployment/runtime machinery out of `accumulated_instruments/` and into `annexation_procedures/`.

`annexation_procedures/` is the operational half of the Machine-Soul assimilation system: it owns the machinery required to install, configure, inspect, and orchestrate bringing a machine into the desired state. The canonical configuration content remains separately browsable under `assimilation_directives/`.

`accumulated_instruments/` is reserved for useful tracked tools, programs, and scripts that are worth keeping in the repository but are not intrinsically part of the Machine-Soul assimilation system.

## Requirements

- Relocate the shared Python runtime currently under `accumulated_instruments/machine_soul/` into `annexation_procedures/`.
- Relocate the broad orchestrator currently at `accumulated_instruments/manage_machine_soul.py` into the operational tree, with `annexation_procedures/manage_machine_soul.py` as the intended human-facing entry point unless a concrete technical constraint discovered during implementation requires a narrowly justified adjustment.
- Choose the shallowest technically clean Python package structure for the shared runtime inside `annexation_procedures/`.
- Treat `annexation_procedures/` as belonging to the Machine-Soul Python operational system for the current architecture; do not add an extra conceptual containment layer merely to anticipate a hypothetical future requirement.
- Preserve the existing separation in which canonical configuration files live under `assimilation_directives/` while operational machinery lives under `annexation_procedures/`.
- Update Python imports, wrapper bootstrapping/import behavior, orchestration loading, tests, CI paths, documentation, and agent-facing architecture notes affected by the relocation.
- Remove active documentation or guidance that describes `accumulated_instruments/machine_soul/` as the Machine-Soul shared runtime location.
- Preserve historical migration documentation when its old paths are genuinely historical; do not rewrite history merely to remove old path strings.
- If `accumulated_instruments/` becomes empty of substantive tools, keep only whatever minimal placeholder/documentation is useful to preserve and explain its intended future role.

## Constraints / non-goals

- This is a taxonomy and relocation cleanup, not a behavioral redesign of the Python runtime.
- Do not change the configuration-deployment safety contract, application declaration model, operation semantics, result model, target-account semantics, or orchestration behavior except where a relocation exposes an actual defect that must be fixed to preserve existing behavior.
- Do not create a new nested Machine-Soul root under `annexation_procedures/` solely because such a structure might become useful later.
- Do not move canonical application configuration out of `assimilation_directives/`.
- Do not repurpose `accumulated_instruments/` to justify its continued existence; it may remain mostly or completely empty until genuinely unrelated reusable tools belong there.
- Do not promote or merge `experimental/v2` to `main`.

## Acceptance criteria

- The authoritative shared Machine-Soul Python runtime no longer lives under `accumulated_instruments/`.
- The broad manager/orchestrator is reachable from the operational `annexation_procedures/` tree.
- Existing per-application declarations and atomic wrappers continue to use one shared runtime implementation rather than duplicating policy.
- Direct wrapper execution, imported wrapper execution, and broad orchestration continue to behave as before.
- Repository documentation clearly communicates the three-way taxonomy:
  - `assimilation_directives/` — canonical configuration content;
  - `annexation_procedures/` — Machine-Soul operational/runtime system;
  - `accumulated_instruments/` — tracked tools not intrinsically part of that system.
- No active runtime, test, CI, or current architectural documentation relies on the old `accumulated_instruments/machine_soul/` or `accumulated_instruments/manage_machine_soul.py` locations.
- Relevant CI remains green after the relocation.

## Validation

- Run the Python unit/integration test suite covering application loading, wrappers, configuration/install operations, orchestration, state, discovery, and repository parity.
- Run platform operation tests applicable to the changed import/entry-point surface on both Linux and Windows through CI.
- Exercise the relocated broad manager and representative atomic wrappers in both standalone and imported paths.
- Search current runtime/tests/CI/current documentation for stale references to the old runtime/orchestrator paths and review any remaining matches as intentionally historical.
- Verify the final repository tree makes the operational relationship between the orchestrator, shared runtime, and per-application procedures discoverable without requiring `accumulated_instruments/`.
