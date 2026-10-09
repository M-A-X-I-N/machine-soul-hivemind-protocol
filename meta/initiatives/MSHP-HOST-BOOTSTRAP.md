# MSHP-HOST-BOOTSTRAP — Host-aware bulk installation and interactive selection

**Status:** OPEN

## Goal

Make fresh-machine annexation an inspectable one-session workflow: preselect packages from host profiles, permit deselection, and install multiple chosen apps without repeating manual per-app navigation.

## Current state / coverage

The broad manager already discovers and invokes atomic application wrappers and supports several multi-app configuration/status workflows, but host-selected desired installation sets and bulk install selection are not established.

## Known gaps

- Declarative install selection model independent of configuration file selection.
- General interactive multi-select package install UI.
- Host-specific initial selection with toggle/preview/confirm UX.
- Safe fresh-clone/fresh-host validation and resumability.

## Deliberate boundaries / deferred work

- No automatic install merely by cloning or discovering a host.
- Begin with empty host-installation templates; the maintainer will explicitly select desired software later. Do not auto-populate them from installed package inventories.
- Do not let bulk flows bypass per-operation provenance, scope, dependency, cancellation or partial-failure safety.

## Related executable tasks

- [`MSHP-ANNEX-BULK-A-010`](../tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-010.md)
- [`MSHP-ANNEX-BULK-A-020`](../tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-020.md)
- [`MSHP-ANNEX-BULK-A-030`](../tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-030.md)
- [`MSHP-ANNEX-BULK-A-040`](../tasks/MSHP-ANNEX-BULK-A/MSHP-ANNEX-BULK-A-040.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

An intentionally selected or host-preselected collection can be reviewed and installed safely in one workflow with tested result reporting and retries.
