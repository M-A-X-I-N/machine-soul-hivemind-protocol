# MSHP-AGENT-BASELINE-B-010 — Specify v1 agent instruction topology and precedence

## Description

Turn the approved design direction into an explicit v1 instruction contract before moving existing MSHP rules. The design should optimize for ChatGPT Chat while remaining ordinary Markdown and avoiding unnecessary platform-specific machinery.

## Requirements

- Define the role and expected size/content of root `AGENTS.md` as the universal entry point.
- Define the role of `.agents/README.md` as an instruction/memory routing map rather than a second monolithic policy file.
- Define separate namespaces for generic baseline instructions, repository-local instructions, and non-normative agent memory.
- Define precedence explicitly: current higher-priority human/system instructions remain above repository policy; applicable repository-local instructions override conflicting baseline instructions; silence in local policy does not cancel baseline policy.
- Define how local overrides should identify what baseline behavior they replace or tighten without copying/re-editing the baseline rule itself.
- Define which instruction subjects should be grouped together based on access patterns rather than aesthetic symmetry.
- Define which instructions are always-read, substantial-work-read, or subject-triggered.
- Define the rule that memory files are knowledge, not instructions, and are loaded only when relevant.
- Avoid depending on nested `AGENTS.md`, `AGENTS.override.md`, Codex-only discovery, or other platform-specific behavior unless a measured/strong performance benefit justifies it.
- Record the contract durably in the task workspace and promote any final generic design decisions into human-facing documentation when appropriate.

## Constraints / non-goals

- Do not move/refactor existing MSHP instructions yet.
- Do not modify `M-A-X-I-N/template` yet.
- Do not design automatic baseline synchronization or version manifests.
- Do not optimize for file-count symmetry; optimize for agent comprehension, routing, and context cost.
- ChatGPT Chat is the primary target; compatibility with other agents is desirable but secondary.

## Acceptance criteria

- A concrete v1 file/topology proposal exists.
- Instruction precedence and override semantics are unambiguous.
- Each proposed file has a clear read trigger and ownership class.
- The design explains why each split improves agent behavior/context rather than merely organization.

## Validation

- Walk the proposed read path for a trivial edit, substantial task, Git operation, task-state change, and architecture investigation.
- Confirm no scenario requires reading the entire `.agents/` tree by default.
- Confirm local policy can override baseline without editing baseline files.
