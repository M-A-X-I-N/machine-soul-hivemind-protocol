# MSHP-DEV-A-070 — Synthesize runtime/version-management findings

## Description

Compare the runtime investigations and determine what reusable Machine-Soul concepts are actually justified. Resist inventing abstractions merely because the subjects share the word runtime.

## Requirements

- Compare version coexistence, desired version sets, selected/default version, manager/backend identity, executable discovery, install scope, architecture, update, and uninstall across Lua/Python/Node.
- Distinguish accidentally multiple candidates from deliberately desired simultaneous versions.
- Identify concepts common enough to deserve shared annexation model/strategy support.
- Identify concepts that must remain runtime/backend specific.
- Decide whether first-class desired-version-set state, version-manager delegation, or selected/default-version state is justified now.
- Identify how installation discovery/provenance would need to evolve for intentionally managed multiple versions.
- Use the additional-runtime survey to ensure any abstraction does not obviously block likely future subjects.
- Create bounded implementation tasks only where evidence supports near-term value.
- Update MSHP-DEV-ENV with deferred version-manager/runtime gaps.

## Constraints / non-goals

- Do not implement runtime integrations in this synthesis task.
- Do not force all runtimes into one abstraction.
- Do not create tasks for unsupported runtimes merely to make the abstraction look complete.
- Do not sacrifice multiversion capability for single-version convenience.

## Acceptance criteria

- An evidence-based runtime/version-management architecture, or explicit decision to avoid one, exists.
- Any implementation tasks are traceable to concrete findings.
- Future runtime/version-manager gaps remain structured non-executable initiative state.

## Validation

- Trace every shared concept to multiple ecosystems or a compelling generic safety requirement.
- Walk simultaneous-version, selected/default, manager-switch, and uninstall-one-version scenarios.
