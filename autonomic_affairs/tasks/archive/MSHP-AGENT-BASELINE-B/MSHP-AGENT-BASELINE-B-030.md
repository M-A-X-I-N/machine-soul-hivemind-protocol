# MSHP-AGENT-BASELINE-B-030 — Design and extract MSHP-local policy and memory boundaries

## Description

Build the complementary local side of the v1 architecture: explicit MSHP repository policy plus a clear distinction between normative local instructions and non-normative memory.

## Requirements

- Identify all current MSHP-specific instructions that were excluded from the generic baseline.
- Design the smallest useful MSHP-local policy set, with `REPOSITORY.md` or equivalent as the default home for project identity/source-of-truth/layout/safety rules.
- Create additional local policy files only when their retrieval/access pattern clearly justifies a split.
- Define how an MSHP-local rule explicitly overrides or tightens a baseline rule.
- Separate normative local policy from `.agents` memory such as architecture notes, decisions, investigations, platform/tool scar tissue, and historical evidence.
- Choose a clear memory namespace/layout under `.agents` without forcing empty categories that provide no value.
- Produce a migration map for current `.agents` files: baseline instruction, local instruction, memory, historical/archive reference, or unchanged external human documentation.
- Keep current source-of-truth relationships explicit.

## Constraints / non-goals

- Do not create mirror local files merely to say 'same as baseline'.
- Do not turn project memory into normative instructions.
- Do not delete uncertain historical knowledge.
- Do not modify the template repository.

## Acceptance criteria

- MSHP's repository-specific policy has an explicit future home separate from baseline instructions.
- Instruction versus memory classification is clear for every current `.agents` document category.
- Local override semantics are demonstrable without modifying baseline files.

## Validation

- Walk current MSHP-specific rules from old locations to proposed local destinations.
- Check that no baseline candidate must contain Machine-Soul-specific policy to remain understandable.
- Check that memory remains discoverable but is not implied mandatory reading.
