# Agent workflow and recovery conventions

## Checkpoint discipline

For repository-changing work:

1. inspect the active branch/current state;
2. read `../autonomic_affairs/agent_tasks.md`, inspect Dispatch, and open the linked detailed task specification;
3. when claiming dispatched work, change its index state to `IN_PROGRESS` and remove it from Dispatch;
4. keep each checkpoint narrow enough to explain and revert independently;
5. run the smallest validation that genuinely proves the changed surface;
6. commit/push meaningful completed work promptly;
7. when a task completes, set it to `COMPLETE`, then populate Dispatch with the next authorized/eligible work in priority order;
8. persist expensive reusable discoveries under `.agents/`.

Do not leave substantial completed work only in an ephemeral tool session.

## Interrupted-session recovery

Do not assume the last narrated action reached the repository. Inspect branch heads/history, compare `../autonomic_affairs/agent_tasks.md` plus the relevant linked task specification with actual commits/files, distinguish committed work from orphaned/reasoning-only work, and validate recovered state before continuing.

Prefer recovering already-created correct Git objects over recreating them manually.

## Source-of-truth discipline

When information conflicts, prefer the source that owns the subject:

1. tracked configuration/source for implemented behavior;
2. human-facing architecture/policy docs for durable design;
3. `autonomic_affairs/agent_tasks.md` for scheduling/state/Dispatch and its linked task files for execution specifications;
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

Follow `../AGENTS.md` and [`PROVENANCE.md`](PROVENANCE.md). Resolve the authoring agent variant through the canonical registry before creating a wholly agent-authored substantive commit. If the variant is unnamed/unregistered, follow the `UNNAMED` notification/ask rules rather than inventing a designation.
