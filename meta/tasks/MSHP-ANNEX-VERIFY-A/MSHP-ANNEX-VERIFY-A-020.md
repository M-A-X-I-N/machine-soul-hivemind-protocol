# MSHP-ANNEX-VERIFY-A-020 — Add origin expectation warnings to supported installers

## Description

Add a conservative, reusable pre-install expected-source verification mechanism once the trust model is accepted.

## Requirements

- Integrate declarative per-application expectations, explicit warnings/refusal options, observable evidence and tests for an official Contour GitHub release URL versus a mismatched host; apply only where package metadata supports it.

## Constraints / non-goals

- Depends on validated design; never silently treat an unverified URL as trusted.

## Acceptance criteria

- Supported install paths present clear mismatch warnings while unrelated valid installs remain compatible.

## Validation

- Inspect current source/architecture and authoritative references relevant to the task.
- Record reproducible findings or targeted validation evidence; explicitly flag untestable claims.
