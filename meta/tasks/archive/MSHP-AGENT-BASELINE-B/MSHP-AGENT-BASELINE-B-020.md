# MSHP-AGENT-BASELINE-B-020 — Extract the generic workflow instruction set

## Description

Use the B-010 topology to extract the generic agent workflow from current MSHP instructions into candidate baseline-owned documents inside MSHP.

## Requirements

- Audit current root `AGENTS.md`, `.agents/README.md`, `.agents/WORKFLOW.md`, `.agents/PROVENANCE.md`, and related lifecycle instructions against the B-010 contract.
- Extract generic rules governing startup/read order, autonomy/interruption, task execution, Dispatch, Active claims, recovery, lineages, checkpoints, validation, history safety, reminders, initiatives, knowledge placement, and provenance.
- Keep generic rules concise while preserving important safety/coordination semantics.
- Remove MSHP-specific directory names, application/runtime policy, concrete CI check IDs, Machine-Soul safety laws, and other project-specific behavior from the baseline candidates.
- Combine subjects that are normally needed together; split subjects with genuinely different retrieval triggers.
- Ensure each baseline file states its scope/read trigger where useful.
- Preserve a traceability map from old MSHP instruction sections to their new generic or local destination.
- Store candidate baseline files and extraction notes in MSHP only.

## Constraints / non-goals

- Do not modify `M-A-X-I-N/template`.
- Do not yet delete or replace current authoritative MSHP instruction files.
- Do not weaken a rule merely to make it shorter.
- Do not carry historical investigations/scar tissue into baseline policy.

## Acceptance criteria

- A complete candidate generic instruction set exists.
- Every significant current MSHP instruction is classified as generic, local, memory, historical, or intentionally dropped.
- The candidate retains the collaboration/workflow behavior the maintainer relies on without importing Machine-Soul-specific policy.

## Validation

- Diff/compare the candidate against current governing instructions by semantic topic.
- Check for accidental MSHP-specific paths/check IDs/application assumptions.
- Simulate recovery and authorized task progression using only the candidate generic rules plus an imagined local profile.
