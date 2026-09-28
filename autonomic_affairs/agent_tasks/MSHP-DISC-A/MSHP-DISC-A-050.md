# MSHP-DISC-A-050 — Synthesize discovery roadmap

## Description

Synthesize the completed DISC-A investigations and applied-check normalization into the next executable implementation roadmap.

Do not guess the implementation topology in advance. Let the evidence from installation discovery and effective-configuration research determine how many generic framework tasks, platform tasks, strategy tasks, or application-specific batches are actually warranted.

## Requirements

- Read the outputs/workspace material from `MSHP-DISC-A-020` and `MSHP-DISC-A-030`, plus the implemented/validated result of `MSHP-DISC-A-040`.
- Reconcile those findings with the shared model established by `MSHP-DISC-A-010`.
- Distill durable architecture decisions into normal documentation and expensive reusable platform/application knowledge into `.agents/`.
- Keep purely historical/raw investigation material in the DISC-A workspace for eventual block archival rather than promoting everything permanently.
- Identify the smallest coherent implementation phases for:
  - richer installation discovery/provenance;
  - effective configuration verification;
  - shared result/evidence presentation where needed;
  - application/platform-specific strategies/hooks proven necessary by the investigations.
- Create sufficiently specified executable follow-on task files and index rows for those implementation phases.
- Assign dependencies based on actual structural prerequisites rather than desired execution order.
- Preserve the future installation-takeover feature as a separate reminder unless the human explicitly promotes it.
- If investigations show the architecture should materially change from the model in `MSHP-DISC-A-010`, document the reason and update the durable design rather than forcing implementation into the earlier hypothesis.

## Constraints / non-goals

- Do not implement the newly created roadmap tasks in the same task unless a tiny documentation/link fix is required to make the roadmap coherent.
- Do not manufacture one implementation task per application when reusable strategy groupings are better.
- Do not force installation and effective-config work into identical implementation shapes.
- Do not silently promote installation takeover into executable work.
- Do not retain raw research as permanent `.agents/` memory without continuing value.

## Acceptance criteria

- There is a concrete, executable next-phase task roadmap derived from evidence rather than speculation.
- Every follow-on task has proper task-schema sections, dependencies, validation, and a bounded implementation surface.
- Durable findings are promoted; temporary investigation material remains clearly temporary/historical.
- Installation takeover remains separate unless explicitly authorized.
- The DISC-A block can be archived later without losing information needed for the implementation phase.

## Validation

- Trace each created implementation task back to specific investigation findings or already-implemented structural-check needs.
- Verify no follow-on task depends on workspace material without linking/identifying it.
- Review task dependencies for genuine structural necessity.
- Confirm the active index and Dispatch remain consistent with the repository task contract.
