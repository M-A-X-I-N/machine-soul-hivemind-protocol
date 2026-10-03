# MSHP-DEV-A-110 — Synthesize runtime package-manager findings

## Description

Compare LuaRocks, pip, and npm and determine whether Machine-Soul needs reusable concepts for interpreter/runtime-bound package environments and desired package inventories.

## Requirements

- Compare package-manager tool ownership, runtime binding, environment/tree identity, scope, package inventory, install/uninstall, credentials, and machine-specific/native-build concerns.
- Identify concepts common enough for reusable annexation machinery.
- Determine whether package inventories should be first-class desired state, optional per-environment capability, or deferred.
- Define how package environments reference the exact runtime/version they belong to.
- Distinguish global/user environments from project-local environments and unmanaged ephemeral environments.
- Create bounded implementation tasks only where at least one near-term ecosystem needs them and evidence supports the abstraction.
- Update MSHP-DEV-ENV with future manager/environment gaps.

## Constraints / non-goals

- Do not implement package managers in this synthesis task.
- Do not automatically claim project dependency management.
- Do not create a universal package abstraction that erases important environment semantics.
- Do not create tasks for every language package manager.

## Acceptance criteria

- An evidence-based package-environment/inventory architecture, or explicit decision to defer one, exists.
- Runtime binding and exact environment identity remain first-class.
- Any implementation tasks are bounded and traceable.
- Unsupported ecosystems remain initiative gaps.

## Validation

- Trace shared concepts across LuaRocks/pip/npm.
- Walk multiversion runtime, multiple environment/tree, global/user, and unmanaged-project scenarios.
