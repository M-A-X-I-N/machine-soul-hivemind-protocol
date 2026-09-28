# MSHP-INST-B-050 — Implement Apt machine scope

## Description

Apply the common scope/ownership lifecycle to the current Apt backend.

Apt/dpkg is a fixed machine-scoped backend; sudo/root is only the execution mechanism.

## Requirements

- Make `AptPackage`'s fixed MACHINE scope participate in the scoped install/check/uninstall lifecycle.
- Persist new Apt ownership in the host/machine provenance namespace.
- Use dpkg discovery's existing machine-scope candidate evidence for post-install and pre-uninstall exact matching.
- Ensure target account does not become semantic owner of the system package merely because it requested installation.
- Permit execution through root/sudo as before without changing scope.
- Implement safe reconciliation for legacy Apt provenance:
  - only upgrade a scope-less legacy record when current exact dpkg discovery proves the same package candidate at fixed machine scope;
  - detect/refuse conflicting duplicate legacy account records rather than arbitrarily choosing one;
  - preserve recoverability and do not delete uncertain state.
- Ensure a machine-scoped managed install is visible as managed regardless of which logical account later performs a check, subject to normal permissions/context.
- Keep existing Apt install/uninstall safety and dry-run behavior.

## Constraints / non-goals

- Do not add Flatpak, Homebrew, pipx, Snap, Nix, or other Linux managers.
- Do not add user-scoped Apt semantics.
- Do not treat sudo identity as installation ownership.
- Do not implement takeover/adoption of pre-existing unmanaged apt packages.

## Acceptance criteria

- Apt is explicitly fixed MACHINE scope end to end.
- New Apt provenance is host/machine scoped.
- Compatible legacy Apt provenance can be reconciled safely; conflicts refuse migration.
- Machine ownership is not duplicated per target account.
- Existing Fish Apt lifecycle remains green.

## Validation

- Unit-test install/check/uninstall from normal/root-like target contexts with one shared machine record.
- Test legacy reconciliation and conflicting legacy records.
- Test dry-run and sudo/root command construction remains correct.
- Run Linux install/discovery/application tests and full CI.
