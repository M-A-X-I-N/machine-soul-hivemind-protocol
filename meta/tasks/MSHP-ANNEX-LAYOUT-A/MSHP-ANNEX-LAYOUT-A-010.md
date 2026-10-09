# MSHP-ANNEX-LAYOUT-A-010 — Design minimal per-application annexation directory layout

## Description

Inspect the annexation root and specify a reversible layout that leaves application directories and only unavoidable top-level files while moving reusable shared internals into a dedicated hidden directory.

## Requirements

- Classify modules/packages, wrappers, tests and import consumers; evaluate Python dotted-hidden-directory import complications and select a Python-safe import mechanism/name; record exact proposed tree.

## Constraints / non-goals

- Do not move code in the planning phase; do not assume hidden Python directories are importable packages.

## Acceptance criteria

- An approved layout plan identifies all affected paths, coupling and rollback requirements.

## Validation

- Inspect relevant source, documentation and supported-platform evidence.
- Preserve findings, counterexamples and proposed validation commands in the task workspace.
