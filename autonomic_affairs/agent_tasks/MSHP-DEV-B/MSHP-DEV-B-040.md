# MSHP-DEV-B-040 — Implement Python multiversion backend

## Description

Implement Windows Python runtime annexation using the official Python Install Manager as the initial backend for USER-scoped multiversion lifecycle.

## Requirements

- Manage/discover the Python Install Manager separately from runtime instances.
- Use the manager's machine-readable inventory and exact runtime tags for managed-runtime discovery.
- Support a desired set of exact manager tags, including architecture/flavor/distributor dimensions exposed by the manager.
- Implement install, exact uninstall, post-mutation rediscovery/verification, and selected/default runtime reconciliation through the manager's native configuration/commands.
- Prefer unambiguous manager invocation rather than assuming a legacy `py` launcher is the modern manager.
- Preserve unmanaged/legacy Python installations as visible but unowned candidates.
- Respect the official manager's USER-scoped runtime model.
- Add fake-runner/unit coverage for simultaneous versions, default changes, legacy launcher collision, unmanaged candidates, and exact uninstall.

## Constraints / non-goals

- Do not manage pip package inventories in this task.
- Do not invent per-machine Python runtime support that the official manager does not provide.
- Do not adopt unmanaged Python installations automatically.
- Do not mutate project virtual environments.
- Do not set maintainer-specific desired Python versions in repository-wide configuration unless already supplied elsewhere.

## Acceptance criteria

- Machine-Soul can represent and reconcile multiple manager-owned Python runtimes safely.
- Default selection is native-manager state separate from runtime installation.
- Unmanaged Python remains discoverable without becoming owned.
- Runtime provenance survives rediscovery and exact uninstall.

## Validation

- Use the completed Python investigation as the behavioral contract and re-check current official manager semantics where commands have changed.
- Exercise at least two installed versions plus one unmanaged candidate in tests.
- Run the repository Python validation suite.
