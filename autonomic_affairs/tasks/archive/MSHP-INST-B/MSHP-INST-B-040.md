# MSHP-INST-B-040 — Implement scoped WinGet mutation

## Description

Apply the common scope/ownership lifecycle to WinGet.

Machine-Soul must explicitly select user or machine scope for managed WinGet operations so WinGet settings/preferences cannot silently change MSHP semantics.

## Requirements

- Map required Machine-Soul USER/MACHINE scope to WinGet's explicit `--scope user|machine`.
- Pass scope explicitly to WinGet install and uninstall commands.
- Make WinGet discovery query user and machine scopes separately and produce distinct scoped correlation candidates so coexisting installations remain visible.
- Keep exact package ID/source filters and non-interactive behavior.
- Correlate scoped WinGet evidence with native ARP/MSIX/AppX evidence where useful without claiming historical WinGet acquisition.
- Ensure current-user AppX/MSIX `PACKAGE_USER` evidence is compatible with a required USER policy for the intended current target account.
- Preserve package/native identity needed to distinguish user and machine candidates.
- Update `_state_matches`/equivalent ownership matching to include scope/native identity through the common scoped lifecycle.
- Add exact scoped uninstall behavior; if WinGet/native discovery cannot uniquely identify the owned candidate, refuse removal.
- Update Oh My Posh's Windows strategy to the evidence-supported explicit scope.
- Treat current Oh My Posh AppX/MSIX manifest behavior as a regression case: its current manifest lacks explicit `Scope:`, so tests must prove the Machine-Soul behavior through explicit WinGet arguments and compatible native package-user evidence rather than manifest assumptions.
- Ensure managing WinGet's own future settings cannot alter Machine-Soul-controlled scope.
- Record dry-run argv including explicit scope.

## Constraints / non-goals

- Do not implement other-user WinGet user-scope mutation.
- Do not manage AppX provisioning.
- Do not implement full all-user MSI inventory.
- Do not infer historical acquisition from WinGet correlation.
- Do not implement installation takeover.

## Acceptance criteria

- Every Machine-Soul-managed WinGet mutation has an explicit scope.
- User and machine WinGet candidates can coexist distinctly.
- Ambient WinGet scope preferences cannot change managed scope.
- Scoped uninstall targets only the owned scope/candidate.
- Oh My Posh remains installable/checkable/removable under the explicit scoped contract with regression coverage.

## Validation

- Unit-test install/uninstall argv for USER and MACHINE.
- Test scoped list discovery for user-only, machine-only, both, and unavailable backend cases.
- Test USER compatibility with current-user AppX `PACKAGE_USER`.
- Test OMP current-manifest-shaped fixture and post-install verification.
- Run Windows install/discovery/application tests and full CI.
