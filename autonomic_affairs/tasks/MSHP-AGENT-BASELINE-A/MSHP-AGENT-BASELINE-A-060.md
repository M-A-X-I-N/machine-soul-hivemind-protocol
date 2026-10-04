# MSHP-AGENT-BASELINE-A-060 — Investigate versioning, compatibility, and migration policy

## Description

Investigate versioning and compatibility policy for a cross-repository baseline before any shared infrastructure is implemented.

## Requirements

- Research versioning options for file baselines and shared executable components, including moving branches, immutable commit SHAs, tags/releases, semantic or schema versions, and migration identifiers.
- For reusable GitHub Actions/workflows, document security and reproducibility tradeoffs of branch/tag/SHA references using current GitHub guidance.
- Determine whether a machine-readable baseline manifest/version file would materially help update discovery, migration ordering, compatibility checks, or diagnostics.
- Research how baseline schema changes versus implementation-only changes could be distinguished.
- Consider compatibility between repositories that intentionally remain on older baseline versions and centrally shared executable components that continue evolving.
- Consider rollback and recovery requirements for failed baseline migrations.
- Identify what version information should be visible to humans/agents during fresh-session/recovery work.
- Preserve findings only in MSHP.

## Constraints / non-goals

- Research only. Do not create releases/tags, manifests, migration files, or shared workflow versions.
- Do not assume semantic versioning is automatically the right model.
- Do not choose moving `main` references merely for convenience if reproducibility/security argues otherwise.

## Acceptance criteria

- Versioning candidates and tradeoffs are documented for both copied/bootstrap files and live shared components.
- Compatibility/migration/rollback concerns are explicit.
- The research is sufficient for the final synthesis to recommend a coherent version model without further basic mechanism discovery.

## Validation

- Cross-check GitHub Actions reference-security claims against current official documentation.
- Verify the analysis handles intentionally lagging repositories and rollback, not only latest-version consumers.
