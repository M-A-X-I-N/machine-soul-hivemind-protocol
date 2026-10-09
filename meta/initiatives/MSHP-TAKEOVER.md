# MSHP-TAKEOVER — Explicit adoption and takeover of unmanaged applications

**Status:** OPEN

## Goal

Investigate and implement safe, explicitly authorized takeover of existing installations, including cases requiring migration to a preferred package/installer method.

## Current state / coverage

Discovery distinguishes present from managed installations, and existing ownership safeguards intentionally prevent silently managing arbitrary pre-existing programs. Earlier takeover intent was recorded only as a reminder.

## Known gaps

- Cross-backend identity/equivalence proof and in-place adoption cases.
- Application state, installer scope and destructive migration risk assessment.
- Dry-run/approval, rollback, ownership transitions and safe pilot implementations.

## Deliberate boundaries / deferred work

- Discovering installation is not permission to claim it.
- No blanket MSI/EXE uninstall and reinstall without preservation and recovery proof.
- Research/design checkpoints must surface safety-sensitive implementation decisions.

## Related executable tasks

- [`MSHP-TAKEOVER-A-010`](../tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-010.md)
- [`MSHP-TAKEOVER-A-020`](../tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-020.md)
- [`MSHP-TAKEOVER-A-030`](../tasks/MSHP-TAKEOVER-A/MSHP-TAKEOVER-A-030.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

At least bounded reviewed takeover paths work and their failure/refusal contract is proven; larger unsafe cases either gain separately scoped tasks or remain explicitly unsupported.
