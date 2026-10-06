# MSHP-HOUSEKEEPING-A-040 — Audit repository-wide consistency and weirdness

## Description

Perform a broad tracked-file consistency pass for stale, contradictory, duplicated, misleading, broken, or obviously obsolete repository material after the task/archive cleanup.

## Requirements

- Inspect all tracked text/source files to the extent practical.
- Look for dead/stale internal links, obsolete paths/branch names, superseded source-of-truth claims presented as current, contradictory lifecycle terminology, duplicated current authority, outdated examples, orphaned navigation, stale references to moved files, obvious structural breakage, and migration wording that has outlived the migration.
- Fix issues that are clearly wrong and low-risk.
- Record uncertain findings rather than cleaning them speculatively.
- Keep historical evidence historical rather than rewriting it into present tense.

## Constraints / non-goals

- Err on the side of caution when unsure whether material is stale or intentionally historical.
- Do not invent new architecture/policy solely to make the repository look tidy.
- Do not delete durable knowledge whose relevance is uncertain.
- Do not rewrite Git history.
- Leave the deeper .agents memory/instruction audit to MSHP-HOUSEKEEPING-A-050 except where a cross-repository inconsistency is obvious.

## Acceptance criteria

- High-confidence repository-wide inconsistencies found by the audit are corrected.
- Uncertain findings are captured durably without speculative deletion.
- Current navigation/source-of-truth relationships are coherent after archival changes.

## Validation

- Re-run representative repository-wide searches for retired paths/terms and moved task blocks.
- Check internal Markdown links/navigation where practical.
- Review changed source-of-truth documents together for contradiction.
