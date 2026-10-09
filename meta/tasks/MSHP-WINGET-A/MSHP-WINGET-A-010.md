# MSHP-WINGET-A-010 — Investigate Microsoft Store packages through WinGet

## Description

Investigate whether and how Microsoft Store-backed WinGet packages differ materially from ordinary WinGet packages for Machine-Soul discovery, provenance, ownership, install, update, and removal.

## Requirements

- Use current official Microsoft/WinGet documentation and current CLI behavior.
- Map `msstore` source identity, package identifiers, agreements, account/licensing dependencies, scope behavior, install/update/uninstall semantics, and machine-readable discovery.
- Specifically establish what generated-looking Store IDs mean, their underlying identifier formats, stability, whether product/store IDs or alternative identifiers can be used for deterministic indexing, and which identity WinGet ultimately requires.
- Research source-preference prerequisites for a later Store-first-through-WinGet install policy without assuming a Store package is equivalent to the ordinary WinGet catalog identity.
- Compare the findings against the existing WinGet annexation/provenance model and identify concrete model gaps only when evidence requires them.
- Persist reusable findings and taskify implementation only after the research supports a design.

## Constraints / non-goals

- Do not implement Store-specific behavior in this task.
- Do not assume Store packages are equivalent to ordinary `winget` source packages.
- Do not thaw this task/block without explicit human authorization.

## Acceptance criteria

- A durable Store-via-WinGet behavior map exists.
- Any provenance/ownership changes needed by Machine-Soul are explicit.
- Follow-up implementation work is taskified only if justified.

## Validation

- Cross-check claims against current official sources.
- Prefer harmless discovery/dry-run experiments when useful.
