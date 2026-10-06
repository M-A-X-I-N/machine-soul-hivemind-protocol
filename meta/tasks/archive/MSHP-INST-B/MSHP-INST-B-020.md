# MSHP-INST-B-020 — Implement scoped installation provenance

## Description

Make persisted Machine-Soul installation ownership follow the actual installation scope instead of assuming one install-state record per target account/application.

The state layer must support a user-scoped and a machine-scoped installation of the same application at the same time.

## Requirements

- Bump the install-state schema and add explicit scope/provenance fields sufficient to record:
  - requested/fixed scope policy result;
  - actual verified installation scope;
  - scope subject account when relevant;
  - manager/backend identity;
  - package/product identity;
  - exact native/uninstall identity when available;
  - backend-specific metadata needed for exact candidate matching.
- Define canonical scoped state namespaces that permit simultaneous user and machine ownership records for one application/host.
- Machine-scoped provenance must live under a host/machine namespace rather than a requesting target-account namespace.
- User/package-user provenance must live under the host plus relevant subject account.
- Add state APIs to enumerate/read/write/delete scoped ownership records without forcing callers to guess file paths.
- Preserve backward reading of the legacy scope-less per-account `InstallState` format.
- Decode legacy state as scope-unknown/unreconciled; do not silently assign WinGet user or machine scope.
- Provide explicit safe reconciliation/migration primitives so later backend tasks can upgrade legacy records only after discovery proves a unique compatible current installation.
- Avoid destructive migration: if multiple legacy records/candidates conflict, retain evidence and refuse automatic ownership conversion.
- Keep machine-local state under ignored `scratch/`.
- Update tests for simultaneous user+machine records, legacy reads, machine namespace, user namespace, deletion isolation, and malformed/conflicting state.

## Constraints / non-goals

- Do not change WinGet/Apt package-manager commands.
- Do not decide candidate ownership in the generic state layer; it stores/retrieves provenance.
- Do not delete legacy state merely because it lacks scope.
- Do not implement cross-account impersonation.
- Do not add unsupported package managers.

## Acceptance criteria

- One application can have separate machine and user ownership records on the same host.
- Machine provenance is no longer semantically owned by an arbitrary target account.
- Legacy state remains readable but cannot masquerade as scoped authoritative ownership.
- State APIs expose enough exact identity for later candidate matching/uninstall.
- No scoped record deletion can accidentally remove another scope's ownership.

## Validation

- Unit-test state path/schema round trips for user, package-user-compatible subject, and machine scopes.
- Unit-test simultaneous records and independent deletion.
- Unit-test legacy scope-less decode/reconciliation inputs.
- Test malformed/ambiguous migration refusal.
- Run state/config/install tests and full CI.
