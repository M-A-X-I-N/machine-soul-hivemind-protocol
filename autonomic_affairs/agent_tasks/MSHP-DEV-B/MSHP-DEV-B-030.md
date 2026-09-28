# MSHP-DEV-B-030 — Implement runtime annexation core

## Description

Implement the shared runtime-instance model justified by DEV-A without forcing all runtimes through one version manager. Add durable desired-set, selected/default, backend identity, discovery, provenance, and exact lifecycle contracts that concrete runtime backends can implement.

## Requirements

- Add typed model/state for runtime subjects and exact runtime instances.
- Represent deliberately desired installed runtime instances as a set rather than one scalar version.
- Represent selected/default runtime state separately from the installed set.
- Preserve ecosystem-relevant identity dimensions such as version, flavor/distribution, architecture, backend, backend instance key, and direct executable/prefix identity where applicable.
- Add a runtime-backend protocol/strategy boundary for discovery, install, exact uninstall, verification, and selected/default reconciliation.
- Persist runtime-instance ownership/provenance separately from generic package-manager application ownership while reusing existing safety/scope concepts where valid.
- Distinguish explicitly desired multiplicity from accidental/unowned duplicate discovery.
- Make backend switching an explicit migration boundary rather than automatic ownership transfer.
- Add operation/result presentation suitable for multiple simultaneous instances.
- Add unit tests for multiversion desired state, default-only changes, exact removal, unmanaged duplicates, and backend mismatch.

## Constraints / non-goals

- Do not implement Python, Node, or Lua commands in the shared core.
- Do not require one universal runtime manager or one universal installation scope.
- Do not make PATH order the source of truth for selected/default state.
- Do not weaken ordinary application duplicate-candidate safety to accommodate runtimes.
- Do not implement package-environment inventory yet beyond clean extension points needed by DEV-B-070.

## Acceptance criteria

- The core can represent and reconcile multiple owned runtime instances without treating them as ambiguity.
- Selected/default state is independently modeled and validated.
- Exact backend ownership prevents unsafe uninstall or silent manager transfer.
- Existing application installation/provenance behavior remains compatible.

## Validation

- Add focused model/state/operation tests plus migration/serialization coverage.
- Exercise simultaneous-version, selected-runtime removal/refusal, and backend-mismatch scenarios.
- Run the repository's Python validation suite.
