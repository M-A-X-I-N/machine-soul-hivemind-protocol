# MSHP-ANNEX-STRUCTURE — Minimal application-focused annexation directory

**Status:** OPEN

## Goal

Keep the annexation tree intuitively application-centered by housing common internal runtime code in a dedicated, clearly separated internal library directory and leaving only genuinely necessary root entry points.

## Current state / coverage

The current Python library-first annexation core works but shared library modules and per-application folders coexist directly beneath annexation/. Repository layout policy already separates annexation from tools/ and assimilation/.

## Known gaps

- Review the full shared-library import/dependency graph and select a Python-compatible internal directory strategy.
- Migrate shared internals without breaking module imports, public wrappers, docs or existing CI.

## Deliberate boundaries / deferred work

- A dot-prefixed directory is preferred, but an underscore-prefixed directory is explicitly acceptable. Clear separation of shared library code from per-application directories is the sole naming/layout requirement; choose the safest Python-compatible approach.
- Do not alter the core operation safety model as collateral of a layout-only move.
- The maintainer delegates directory naming to the design task. Escalate material compatibility or public API-breaking questions, not merely a dot-versus-underscore naming choice.

## Related executable tasks

- [`MSHP-ANNEX-LAYOUT-A-010`](../tasks/MSHP-ANNEX-LAYOUT-A/MSHP-ANNEX-LAYOUT-A-010.md)
- [`MSHP-ANNEX-LAYOUT-A-020`](../tasks/MSHP-ANNEX-LAYOUT-A/MSHP-ANNEX-LAYOUT-A-020.md)

Mutable task states, dependencies and Dispatch remain authoritative in [`../tasks.md`](../tasks.md).

## Promotion / closure criteria

The annexation root follows an approved minimal layout, its internal shared library imports work, and regression checks prove semantic parity.
