# MSHP-AGENT-BASELINE-B-040 — Refactor MSHP onto the v1 instruction architecture

## Description

Apply the approved B-010 through B-030 structure to Machine-Soul itself so the architecture is tested against the repository that supplied the workflow.

## Requirements

- Refactor root `AGENTS.md` into the concise entry/routing role defined by B-010 while retaining tiny universally useful repository orientation where beneficial.
- Create the baseline instruction namespace/files inside `.agents` using the B-020 generic content.
- Create the local instruction namespace/files using the B-030 MSHP-specific content.
- Reorganize `.agents` knowledge into the selected memory namespace where doing so improves instruction/memory separation.
- Update links/read-order/source-of-truth references throughout current MSHP governance docs.
- Preserve current task/reminder/initiative/provenance behavior and current Git safety guarantees unless an explicitly approved v1 design intentionally changes their expression.
- Keep baseline-owned and local-owned files independently diffable.
- Do not change product/runtime behavior as part of the instruction refactor.

## Constraints / non-goals

- Do not modify `M-A-X-I-N/template` in this task.
- Do not introduce automatic update/version machinery.
- Do not opportunistically rewrite unrelated project documentation or application code.
- Do not rely on ChatGPT memory of the old layout after the refactor; tracked navigation must stand alone.

## Acceptance criteria

- MSHP operates under the new baseline/local/memory instruction structure.
- Generic baseline files contain no meaningful MSHP-specific policy.
- Local policy can override/tighten baseline without editing baseline files.
- Old authoritative instruction locations either become valid routers or are clearly superseded with no conflicting live authority.

## Validation

- Run repository-wide link/path checks after moves.
- Search for stale references to old `.agents` locations.
- Re-read the complete fresh-session path from root `AGENTS.md` as if no prior chat context existed.
- Verify current task/recovery/provenance scenarios remain expressible under the new structure.
