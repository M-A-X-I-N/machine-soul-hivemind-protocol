# MSHP-INST-A-020 — Investigate Windows installation scope

## Description

Investigate Windows installation-scope behavior and map the abstract semantics from `MSHP-INST-A-010` onto the mechanisms Machine-Soul actually uses or is likely to use first.

WinGet is the primary focus because Machine-Soul already installs Oh My Posh through WinGet and the planned Windows-application investigation may manage WinGet's own settings.

## Requirements

- Use current authoritative Microsoft/WinGet documentation and, where needed, upstream source/manifest behavior.
- Investigate WinGet install and uninstall scope semantics, including:
  - `--scope user` and `--scope machine`;
  - how installer manifests declare/support scope;
  - what happens when requested scope is unavailable;
  - behavior when no explicit scope is supplied;
  - interaction with WinGet `settings.json` scope preferences;
  - whether package-specific installer selection can silently change resulting scope;
  - how `winget list`/discovery distinguishes or fails to distinguish coexisting user/machine instances;
  - how uninstall can target the intended scoped instance safely.
- Explicitly analyze the current MSHP hazard: `WingetPackage` does not pass scope, so managing WinGet's own `installBehavior.preferences.scope` could otherwise change Machine-Soul install behavior.
- Investigate relevant Windows native installation forms that may appear behind WinGet or independently:
  - MSI/ARP machine versus per-user registrations;
  - MSIX/AppX package-user semantics and provisioned/machine concepts where relevant;
  - portable installers when their effective scope is path/user dependent;
  - built-in/OS components where ordinary install scope is not meaningful.
- Determine what scope evidence current Windows discovery backends can reliably observe and what additional fields/backends would be required.
- Investigate execution-account versus target-account behavior for user-scoped WinGet/MSIX-style installs.
- Determine whether cross-account user-scoped installation is safely achievable with currently supported Windows mechanisms or should initially be explicitly unsupported.
- Define the minimum Windows-first implementation surface that can be completed independently from future Linux package-manager support.
- Update `MSHP-INST-SCOPE` with Windows coverage and deliberately deferred Windows edge cases.

## Constraints / non-goals

- Do not install/uninstall software during the investigation.
- Do not mutate WinGet settings.
- Do not assume WinGet correlation proves historical acquisition.
- Do not implement the scope model or flags in this task.
- Do not require complete support for every Windows installer technology before WinGet/core scope can proceed.
- Do not implement installation takeover.

## Acceptance criteria

- WinGet's explicit/default/preference scope behavior is documented well enough to design deterministic Machine-Soul mutation.
- The interaction between MSHP-managed WinGet settings and package installation scope is explicitly addressed.
- Windows discovery/provenance gaps for actual scope are identified.
- Cross-account user-scoped Windows installation has a concrete support recommendation.
- A bounded Windows-first implementation path is identified without relying on future Linux work.

## Validation

- Cross-check all material WinGet scope claims against current official documentation/upstream behavior.
- Walk user-only, machine-only, dual-scope, unsupported-requested-scope, and settings-default-change scenarios.
- Verify proposed uninstall targeting cannot casually remove a different scoped installation than Machine-Soul owns.
