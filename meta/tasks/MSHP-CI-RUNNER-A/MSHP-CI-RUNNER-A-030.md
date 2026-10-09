# MSHP-CI-RUNNER-A-030 — Design a preprovisioned Windows SML worker image

## Description

Specify an immutable-base plus layered/differencing Windows worker image with Satisfactory Mod Loader toolchain already installed.

## Requirements

- Detail provenance of SML/VS/SDK dependencies, repeatable image rebuild, freshness, caching, licensing, rollback, tool versions and image integrity; ensure regular Windows worker and SML variant share base when supported.

## Constraints / non-goals

- Requires runner topology and layered-image research; planning only, no actual Windows image creation.

## Acceptance criteria

- An image build and validation recipe identifies dependencies and expected CI speedups without promising arbitrary compatibility.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
