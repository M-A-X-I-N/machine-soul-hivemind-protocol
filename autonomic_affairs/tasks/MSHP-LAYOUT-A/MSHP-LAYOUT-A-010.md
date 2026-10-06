# MSHP-LAYOUT-A-010 — Rename the generic baseline project-control namespace to meta

## Description

Rename the baseline-reserved top-level project-control namespace from exact lowercase `project/` to exact lowercase `meta/`, then adopt the resulting generic baseline changes into MSHP.

## Requirements

- Update `M-A-X-I-N/baseline` so the reserved generic project-control/collaboration path is exactly lowercase `meta/`.
- Move the baseline seed contents currently under `project/` to `meta/` without changing their ownership semantics.
- Update generic baseline documentation/routing that currently names `project/`, including maintenance/adoption guidance.
- Keep `meta/` exempt from child-repository source-code casing conventions for the same reason `project/` was previously reserved.
- Adopt all changed baseline-managed files into MSHP so its generic baseline surface again matches `M-A-X-I-N/baseline`.
- Do not move MSHP's `autonomic_affairs/` tree yet; that is A-020.

## Constraints / non-goals

- Do not add baseline version/manifest/updater machinery.
- Do not change MSHP-specific local control-plane paths except where needed to adopt the generic baseline wording.
- Do not rename or repurpose `.machine_soul_root`.

## Acceptance criteria

- `M-A-X-I-N/baseline` has no live `project/` namespace and reserves exact lowercase `meta/`.
- Baseline-managed files in MSHP match the canonical generic source after adoption.
- Generic maintenance/adoption instructions describe `meta/`, not `project/`.
- No repository-local state is replaced by baseline seed state.

## Validation

- Compare canonical baseline-managed blobs between `M-A-X-I-N/baseline` and MSHP.
- Search live baseline content for stale `project/` control-path references.
- Walk root → generic router → local router → `meta/` navigation in the template.
