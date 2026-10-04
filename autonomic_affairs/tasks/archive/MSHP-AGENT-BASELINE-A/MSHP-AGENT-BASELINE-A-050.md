# MSHP-AGENT-BASELINE-A-050 — Investigate baseline and repository-local override boundaries

## Description

Research how generic agent infrastructure can remain centrally reusable while each repository preserves project-specific policy, knowledge, CI, and task conventions.

## Requirements

- Use the A-020 inventory and A-030/A-040 mechanism findings as concrete inputs.
- Investigate layering patterns such as generated generic files plus local extension files, include/import conventions where supported, baseline manifests, policy fragments, convention-over-configuration, and clearly separated generic/local directories.
- Determine which MSHP agent surfaces can realistically support layering and which are inherently single-file/human-readable and may require migration/merge semantics instead.
- For root `AGENTS.md`, `.agents/`, provenance, workflow/recovery rules, task schemas, reminders/initiatives, CI selection, and documentation policy, identify plausible generic/local ownership boundaries.
- Identify how conflicts between baseline policy and repository-local policy should be made explicit and which authority should win.
- Consider discoverability for agents: a layered system must remain understandable from a fresh session without requiring opaque generated state.
- Identify anti-patterns that would create accidental forks or hidden local overrides.
- Preserve findings only in MSHP.

## Constraints / non-goals

- Read-only inspection of other repositories is permitted when relevant to research. Do not modify any repository other than MSHP; within MSHP, writes are limited to normal task bookkeeping and storing relevant research/findings.
- Research only. Do not refactor MSHP into the proposed layering model.
- Do not modify any other repository.
- Do not optimize only for deduplication; clarity and explicit authority are primary.
- Do not assume every generic component needs a repository-local override mechanism.

## Acceptance criteria

- A concrete baseline/local ownership analysis exists for each major reusable infrastructure category.
- Authority/conflict rules are explicit for serious layering candidates.
- The analysis identifies components that should remain copied/local rather than shared if layering would be worse.

## Validation

- Walk through the model from a fresh-agent perspective and identify where authority would be ambiguous.
- Check that proposed layering does not silently erase repository-specific policy.
