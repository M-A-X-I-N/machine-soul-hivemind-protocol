# MSHP-DISC-B-040 — Implement native Windows installation discovery

## Description

Implement granular installation discovery for applications running as native Windows applications, using package/native registration and executable evidence without pretending catalog correlation proves historical acquisition.

## Requirements

- Add reusable WinGet installed-package/catalog-correlation discovery for exact declared package identities using the most stable machine-readable interface available without silently creating an undeclared hard dependency.
- Add Windows Add/Remove Programs / MSI registration discovery, including relevant per-user/per-machine and 32/64-bit views needed for current applications.
- Add MSIX/AppX package identity discovery with package family/full-name, version/path, and user/scope information when available.
- Compose executable/path/version observations with registration candidates and de-duplicate/correlate candidates conservatively.
- Wire native Windows discovery plans for Oh My Posh, PowerShell, Windows Terminal, Contour, and CMD.
- Treat CMD as a built-in/platform capability rather than inventing package-manager provenance.
- Preserve side-by-side candidates where legitimate, especially PowerShell host/version differences.
- For Windows Terminal, use verified package-family/distribution identities and retain ambiguity between Store/WinGet/manual acquisition when the platform cannot prove the frontend.
- For Oh My Posh, exact WinGet correlation may establish preferred-strategy compatibility/manageability but must not claim WinGet historically installed it.
- Mark CHECK_INSTALLED supported where a meaningful native discovery plan exists even when Install/Uninstall remain unimplemented.
- Use ../MSHP-DISC-A/workspace/installation_discovery.md as the evidence map.

## Constraints / non-goals

- Do not use display-name fuzzy matching as silent ownership/provenance proof.
- Do not require the optional Microsoft.WinGet.Client module unless this task explicitly documents and justifies that dependency; prefer a dependency-free or capability-detected approach.
- Do not treat WinGet list/correlation as historical installer proof.
- Do not include MSYS2/Cygwin shell discovery; that is MSHP-DISC-B-050.
- Do not mutate installs or registry package records.

## Acceptance criteria

- Native Windows applications return candidate-rich installation assessments from appropriate exact identities.
- ARP/MSI, MSIX/AppX, WinGet correlation, executable evidence, and Machine-Soul ownership remain distinguishable.
- WinGet unavailable or one backend failing does not become false absence when other evidence can exist.
- Side-by-side/ambiguous candidates can be reported safely.

## Validation

- Unit-test representative ARP/MSI, MSIX, WinGet-correlated, executable-only, unavailable-backend, and multi-candidate cases.
- Validate current OMP, PowerShell, Windows Terminal, Contour, and CMD declarations.
- Run Windows application/install tests and full CI.
