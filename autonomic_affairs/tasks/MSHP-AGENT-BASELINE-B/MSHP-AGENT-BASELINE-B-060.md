# MSHP-AGENT-BASELINE-B-060 — Populate the GitHub template with the generic instruction baseline

## Description

Use the validated MSHP reference-consumer structure to create the first practical agent-instruction template for new repositories.

## Requirements

- Before writing, re-inspect `M-A-X-I-N/template` and preserve any unexpected human/concurrent content.
- Populate the template only with the validated generic instruction files and the minimum seed-once local/task/memory skeleton required for the workflow to function.
- Provide a clear local repository-policy placeholder that a new repository is expected to fill in.
- Ensure baseline and local instruction namespaces are separate from first commit.
- Seed empty memory/task/reminder/initiative structures only where the validated instruction workflow actually depends on them.
- Do not copy MSHP-specific paths, tasks, CI checks, application/runtime architecture, or historical memory.
- Do not add automatic updater/version-manifest machinery.
- Keep GitHub-template usability straightforward: the generated repository should make sense by reading root `AGENTS.md` first.

## Constraints / non-goals

- No reusable CI runtime/tooling repository is created.
- No cross-repository updater is implemented.
- No other consumer repository is modified.
- Do not include files merely because MSHP has them.

## Acceptance criteria

- `M-A-X-I-N/template` contains a minimal usable generic instruction baseline.
- A new repository generated from its file tree has an obvious place for local policy without editing baseline rule files.
- The template contains no meaningful MSHP-specific project content.

## Validation

- Compare template baseline files against MSHP baseline-owned files for intended equality/controlled differences.
- Search the template for MSHP-specific identifiers/paths/check IDs.
- Walk the template's root-to-policy-to-task/memory navigation as a fresh repository.
