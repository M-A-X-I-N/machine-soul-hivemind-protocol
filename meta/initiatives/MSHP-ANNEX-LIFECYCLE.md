# MSHP-ANNEX-LIFECYCLE — Update handling and installer source expectations

**Status:** OPEN

## Goal

Extend safe managed application lifecycle beyond Install/Check/Uninstall to explicit updates and confidence that installer sources/manifests match declared expectations.

## Current state / coverage

MSHP has installation discovery, exact owned provenance, backend scope and rollback-oriented config semantics; generic managed updates and proactive source-origin expectation checks are not yet complete.

## Known gaps

- Backend-neutral update intent, version/pin policy and rollout.
- Pre-install manifest/source provenance and URL/redirect expectation warnings.
- Representative WinGet/Apt update and expected-origin implementations after design.

## Deliberate boundaries / deferred work

- No implicit updates during status/discovery.
- A URL allowlist is a warning heuristic, not a signature guarantee.
- Unmanaged installs remain unowned.

## Related executable tasks

- [`MSHP-ANNEX-UPDATE-A-010`](../tasks/MSHP-ANNEX-UPDATE-A/MSHP-ANNEX-UPDATE-A-010.md)
- [`MSHP-ANNEX-UPDATE-A-020`](../tasks/MSHP-ANNEX-UPDATE-A/MSHP-ANNEX-UPDATE-A-020.md)
- [`MSHP-ANNEX-VERIFY-A-010`](../tasks/MSHP-ANNEX-VERIFY-A/MSHP-ANNEX-VERIFY-A-010.md)
- [`MSHP-ANNEX-VERIFY-A-020`](../tasks/MSHP-ANNEX-VERIFY-A/MSHP-ANNEX-VERIFY-A-020.md)
- [`MSHP-WINGET-A-010`](../tasks/MSHP-WINGET-A/MSHP-WINGET-A-010.md)
- [`MSHP-WINGET-A-030`](../tasks/MSHP-WINGET-A/MSHP-WINGET-A-030.md)
- [`MSHP-WINGET-A-040`](../tasks/MSHP-WINGET-A/MSHP-WINGET-A-040.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

Validated update and origin-expectation capabilities exist for selected backend pilots; unsupported cases are explicitly classified and any remaining source-policy gaps accepted or deferred.
