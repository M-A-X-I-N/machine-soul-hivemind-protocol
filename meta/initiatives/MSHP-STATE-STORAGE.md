# MSHP-STATE-STORAGE — Versioned durable host/account application state

**Status:** OPEN

## Goal

Give Machine-Soul an OS-appropriate persistent application state directory on Windows and Linux for ownership records and meaningful operation logs, while retaining scratch only for explicitly ephemeral machine-local material.

## Current state / coverage

MSHP currently uses ignored scratch/ for backups, deployment/installation provenance, temporary state, logs and caches. The source of truth for tracked desired content remains the repository.

## Known gaps

- Research and recommend machine/account state path semantics (Windows local vs roaming AppData and Linux XDG state); the maintainer explicitly left the Windows path decision open for investigation.
- Versioned on-disk schema and forward migration/compatibility behavior.
- Move qualifying provenance and durable action logs without losing exact ownership or state safety.

## Deliberate boundaries / deferred work

- State remains local/private and should not be committed or confused with canonical config.
- Protect sensitive logs and credentials.
- No unreviewed migration of existing state or dropping legacy provenance; keep disposable data under scratch/.

## Related executable tasks

- [`MSHP-STATE-A-010`](../tasks/MSHP-STATE-A/MSHP-STATE-A-010.md)
- [`MSHP-STATE-A-020`](../tasks/MSHP-STATE-A/MSHP-STATE-A-020.md)
- [`MSHP-STATE-A-030`](../tasks/MSHP-STATE-A/MSHP-STATE-A-030.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

Validated versioned durable state API and tested migration preserve existing managed ownership on supported platforms.
