# MSHP-DISC-B-020 — Decouple installation discovery

## Description

Refactor installation discovery into its own declared capability and shared engine rather than deriving check_installed from the application's install_strategy.

Preserve existing Install/Uninstall ownership safety while establishing the reusable observation/candidate pipeline that later platform tasks enrich.

## Requirements

- Add an explicit installation-discovery plan/descriptor surface to PlatformDeclaration that is independent from install_strategy.
- Permit check_installed to be supported when Install and Uninstall are unsupported or not implemented.
- Add reusable discovery descriptor/handler dispatch without application-ID branches in the generic engine.
- Include a generic executable/path/version probe suitable for composition with platform package-registration backends.
- Convert observations into the InstallationCandidate/InstallationAssessment model from MSHP-DISC-B-010.
- Map assessments into stable check_installed OperationResult codes/data while preserving rich candidates/evidence.
- Do not treat preferred-strategy lookup failure as proof of absence.
- Preserve the current Fish/Apt and Oh My Posh/WinGet check behavior through explicit discovery declarations/adapters rather than hidden install-strategy coupling.
- Keep Machine-Soul install-state ownership/provenance as a separate observation/relation.
- Ensure Install/Uninstall preflight behavior continues to refuse casual ownership/removal of pre-existing software and does not regress while richer discovery lands.
- Use the detailed installation evidence findings in ../MSHP-DISC-A/workspace/installation_discovery.md.

## Constraints / non-goals

- Do not implement the full Linux dpkg/Flatpak evidence set here.
- Do not implement Windows ARP/MSIX enumeration here.
- Do not scan arbitrary package managers that no declared application needs.
- Do not infer historical acquisition from catalog/package correlation.
- Do not implement takeover/adoption.

## Acceptance criteria

- check_installed no longer requires install_strategy to exist conceptually or in dispatcher logic.
- Application declarations can describe discovery identities separately from preferred installation strategy.
- Fish and Oh My Posh retain working current detection while using the new architecture.
- The engine can aggregate more than one observation/candidate source.
- Backends can report unknown/ambiguous without collapsing to not_installed.

## Validation

- Add unit tests for discovery-without-install-strategy, preferred managed/unmanaged, no evidence, backend unavailable/unknown, and multiple/conflicting candidate aggregation.
- Retain Install/Uninstall ownership tests.
- Verify generic engines contain no application-ID dispatch.
- Run full CI.
