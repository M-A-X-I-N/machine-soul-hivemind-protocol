# Agent workflow and recovery conventions

## Checkpoint discipline

For repository-changing work:

1. inspect the active branch/current state;
2. read `../TASKS.md` and confirm the current Next task;
3. keep each checkpoint narrow enough to explain and revert independently;
4. run the smallest validation that genuinely proves the changed surface;
5. commit/push meaningful completed work promptly;
6. update `TASKS.md` when global status changes;
7. persist expensive reusable discoveries under `.agents/`.

Do not leave substantial completed work only in an ephemeral tool session.

## Interrupted-session recovery

Do not assume the last narrated action reached the repository. Inspect branch heads/history, compare `TASKS.md` with actual commits/files, distinguish committed work from orphaned/reasoning-only work, and validate recovered state before continuing.

Prefer recovering already-created correct Git objects over recreating them manually.

## Source-of-truth discipline

When information conflicts, prefer the source that owns the subject:

1. tracked configuration/source for implemented behavior;
2. human-facing architecture/policy docs for durable design;
3. `TASKS.md` for global progress/sequencing;
4. root `AGENTS.md` for concise operating rules;
5. `.agents/` for supporting agent workflow/context/discoveries.

## Knowledge capture

Agents do not need permission to add useful knowledge to `.agents/`.

Capture it when rediscovery would be wasteful. Include what was learned, whether it is verified or inferred, enough context to reuse it, useful reproduction/validation commands, and failed approaches when they would otherwise be tempting to repeat.

Do not hide human-relevant architecture exclusively in agent notes; promote it to human-facing docs too.

## Git history preservation

Normal correction is additive: new corrective commits, reverts, fast-forward ref movement, and new branches/checkpoints.

Do not rewrite/discard existing reachable history or unique work without explicit human authorization identifying the affected history/ref and operation.

## Validation

Use real checks matching the changed surface. Documentation/policy changes may be validated by rereading, link/path checks, tree inspection, and consistency review. Add executable tests/checks as implementation appears; do not invent fake build commands before tooling exists.

## Provenance

Follow `../AGENTS.md`. Wholly agent-authored substantive commits from this lineage use an `Agent-authored-by:` trailer containing `Gippity`.
