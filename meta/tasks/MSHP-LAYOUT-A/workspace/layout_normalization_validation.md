# MSHP-LAYOUT-A-050 — Normalized layout validation

## Final live top-level layout

The normalized repository-owned top-level vocabulary is:

```text
meta/
annexation/
assimilation/
tools/
research/
experiments/
assets/
archive/
```

Conventional/tool-defined root surfaces remain separate, including `.agents/`, `.github/`, `.machine_soul_root`, `AGENTS.md`, `README.md`, and ignored `scratch/`.

## Physical migration integrity

The directory moves were performed as Git tree moves before content-reference rewrites.

- `autonomic_affairs/` → `meta/`
- `annexation_procedures/` → `annexation/`
- `assimilation_directives/` → `assimilation/`
- `accumulated_instruments/` → `tools/`
- `acquired_intelligence/` → `research/`
- `arcane_experiments/` → `experiments/`
- `assembled_assets/` → `assets/`
- `abandoned_artifacts/` → `archive/`

The original subtrees were reused directly for each physical move. Content changes were made only afterward where live imports, paths, routing, tests, CI, or documentation required them.

A direct recursive-tree check after the migrations found none of the superseded top-level directories.

## Runtime/configuration migration

The operational Python package/import namespace is now `annexation`.

Canonical tracked desired configuration is now under `assimilation/`.

The A-030 main checkpoint initially exposed one stale repository-parity assertion that still expected `autonomic_affairs/`. Linux and Windows each ran 320 Python tests and failed only that one assertion. The test was corrected to require `meta/`, then the follow-up run passed:

- policy: success;
- Linux validation: success;
- Windows validation: success;
- CodeQL Python: success.

Fresh-clone checks and CodeQL Actions were correctly skipped by the selector on the narrow follow-up commit because their relevant inputs had not changed.

## Support-directory migration

A-040 preserved the original support-directory subtrees, then updated the nine live files that referred to the old names.

Its main-branch validation selected the full suite because the CI selector itself changed. Results:

- policy: success;
- Linux validation: success;
- Windows validation: success;
- fresh-clone Linux: success;
- fresh-clone Windows: success;
- CodeQL Python: success;
- CodeQL Actions: success.

## Stale-reference audit

The audit distinguishes current navigation/dependencies from truthful historical evidence.

### Corrected live authority

Current root/local routing, CI workflows/helpers, code, tests, configuration resolution, human-facing architecture, and navigation use the normalized paths.

Two stale authoritative documents were found during A-050 and corrected:

1. `meta/README.md` still called itself “Autonomic affairs” and still claimed the old all-`a` thematic naming convention.
2. `meta/docs/CROSS_REPOSITORY_AGENT_BASELINE.md` still described the baseline-reserved namespace as `project/` after the canonical baseline had moved to `meta/`.

The root README's section language was also normalized from “directives/procedures” to the shorter assimilation/annexation terminology.

### Agent memory

31 `.agents/memory/` files contained `autonomic_affairs/` path references. Inspection showed these were links/references to docs, tests, initiatives, or archived task material, not historical prose that depended on preserving the obsolete path spelling. They were mechanically repaired to `meta/`.

An old-inventory `project/` hit in `.agents/memory/architecture/developer_annexation.md` is the unrelated phrase “project/external refusal” and is not a baseline path reference.

### Historical exclusions

Files under `meta/tasks/archive/` retain historical path names when those names describe the repository state at the time.

The active `MSHP-LAYOUT-A` task specifications also necessarily describe the source and destination names of this migration. Those mentions are migration evidence rather than unresolved dependencies and will become historical when the block archives.

## Durable layout invariant

`meta/tests/python/test_repository_parity.py` now requires all eight normalized top-level directories to exist and explicitly requires all eight superseded directories to be absent.

The same test continues to require `.machine_soul_root` and `meta/`, preserving the dedicated runtime root sentinel independently of control-plane layout.

## Baseline namespace

The canonical baseline reserves exact lowercase `meta/`; child-repository source naming conventions do not recase it.

MSHP uses that exact path for its repository control plane while retaining repository-owned task/docs/tests/reminder/initiative contents.

A dedicated final canonical-baseline conformance pass remains A-060.

## Result

The normalized layout is internally coherent and has durable regression coverage.

A-050 can complete after the post-audit main-branch validation checkpoint succeeds.
