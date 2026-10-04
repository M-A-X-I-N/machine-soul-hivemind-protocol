# MSHP-AGENT-BASELINE-A-020 — Inventory reusable agent infrastructure in Machine-Soul

## Description

Systematically inventory the agent-related infrastructure already present in Machine-Soul and determine what is actually reusable across repositories versus merely useful here.

## Requirements

- Review root `AGENTS.md`, `.agents/`, task/reminder/initiative lifecycle infrastructure, provenance, lineage/recovery policy, documentation style, CI control-plane concepts, archive rules, and other agent-facing governance surfaces.
- Classify each meaningful component as at least one of: generic reusable baseline; generic with repository-local parameters/extensions; MSHP-specific; historical/scar-tissue only; or not worth sharing.
- Distinguish policy/interface concepts from their current MSHP-specific implementation. Example: a generic CI-selector architecture may be reusable while MSHP check IDs/path relevance are not.
- Identify dependencies among reusable components so later research does not accidentally extract a convention without the rules it relies on.
- Identify any generic infrastructure that is currently duplicated across multiple MSHP files and could conceptually have a clearer baseline/local layering model.
- Record why each classification was chosen and what repository-local information would still be required in a consumer.
- Preserve findings only in MSHP.

## Constraints / non-goals

- Read-only inspection of other repositories is permitted when relevant to research. Do not modify any repository other than MSHP; within MSHP, writes are limited to normal task bookkeeping and storing relevant research/findings.
- Research only. Do not extract/copy infrastructure into `M-A-X-I-N/template` or any other repository.
- Do not modify current MSHP behavior merely because something appears reusable.
- Do not classify content as generic solely because it is agent-related.
- Historical notes may inform the inventory but must not be mistaken for current baseline requirements.

## Acceptance criteria

- A component-level reuse inventory exists with explicit classifications and rationale.
- The inventory distinguishes reusable concepts from MSHP-specific implementation/data.
- The inventory is detailed enough for later distribution/override research to reason from concrete components rather than vague categories.

## Validation

- Cross-check inventory entries against current MSHP source-of-truth documents and repository tree.
- Verify no current MSHP-specific check IDs, paths, applications, machine assumptions, or project architecture are mislabeled as generic without justification.
