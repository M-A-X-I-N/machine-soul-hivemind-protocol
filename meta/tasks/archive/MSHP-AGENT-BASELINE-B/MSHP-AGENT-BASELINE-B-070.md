# MSHP-AGENT-BASELINE-B-070 — Define the manual baseline maintenance and adoption workflow

## Description

Finish v1 by defining the human-plus-agent maintenance workflow that replaces automated baseline synchronization for now.

## Requirements

- Define how a human and agent compare an existing repository's generic baseline files against the current template using Git history/blame/diffs and semantic review.
- Define how to distinguish generic baseline changes from repository-local policy changes.
- Define the expected update sequence: inspect, compare, propose, preserve local overrides, validate, commit.
- Define how to adopt the baseline into an existing repository that did not originate from the template without pretending template ancestry.
- State explicitly that no baseline-version file/manifest is required in v1; Git history plus semantic comparison is accepted as sufficient until actual maintenance pain proves otherwise.
- Define when a future need should reopen the archived A-block synchronization/versioning research.
- Update the durable cross-repository baseline architecture document so its v1 recommendation reflects this deliberately simplified manual model.
- Replace/update the implementation reminder so completed v1 work is not left as stale future intent.
- Close/archive the B block when terminal.

## Constraints / non-goals

- Do not implement automatic synchronization, update bots, manifests, schema migrations, or fleet orchestration.
- Do not migrate arbitrary existing repositories as part of defining the procedure.
- Do not create fake provenance/version state that Git already provides adequately for v1.

## Acceptance criteria

- The manual maintenance/adoption workflow is explicit and recoverable.
- The durable architecture document reflects the simplified v1 scope.
- Future automation is clearly deferred until evidence demonstrates manual maintenance is insufficient.
- The B block closes without leaving duplicate reminder/task authority.

## Validation

- Walk one hypothetical template update and one hypothetical legacy-repository adoption end-to-end.
- Verify the process preserves local overrides without editing the template baseline in-place.
- Verify no v1 step depends on an unimplemented version/updater mechanism.
