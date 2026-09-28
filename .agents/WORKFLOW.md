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

## Task granularity default

Unless the human explicitly requests a particular task structure, agents have broad discretion to choose the task boundaries that function best for the agent actually executing the work. Optimize for coherent implementation, validation, dependency clarity, recoverability, and cross-context survivability. Do not prefer either tiny or large tasks for their own sake; Git/checkpoint overhead is one practical factor among those concerns.

The task system exists primarily to preserve executable intent and intermediate state across context/session boundaries, not to require ceremony for every repository edit.

If a change is isolated from any larger active block and is obviously one natural commit, no task is required. In that case inspect the relevant authority, make the change, validate the changed surface, and commit/push it directly.

Do not use this exception to bypass task state for work that is already part of an active task/block, has meaningful sequencing/dependencies, spans multiple checkpoints, or could plausibly be interrupted between distinct decisions.

## Interrupted-session recovery

Do not assume the last narrated action reached the repository. Inspect branch heads/history, compare `../autonomic_affairs/agent_tasks.md` plus the relevant task specification with actual commits/files, and resolve a known task ID through `../autonomic_affairs/agent_tasks/README.md` when it may already be archived. Distinguish committed work from orphaned/reasoning-only work and validate recovered state before continuing.

Prefer recovering already-created correct Git objects over recreating them manually.

## Source-of-truth discipline

When information conflicts, prefer the source that owns the subject:

1. tracked configuration/source for implemented behavior;
2. human-facing architecture/policy docs for durable design;
3. `autonomic_affairs/agent_tasks.md` for scheduling/state/Dispatch and `autonomic_affairs/agent_tasks/` for active/archived execution specifications plus temporary task workspaces;
4. `autonomic_affairs/initiatives/` for structured non-executable unfinished intent/debt relevant to the active work;
5. root `AGENTS.md` for concise operating rules;
6. `.agents/` for supporting agent workflow/context/discoveries.

## Knowledge capture

Agents do not need permission to add useful knowledge to `.agents/`.

Capture it when rediscovery would be wasteful. Include what was learned, whether it is verified or inferred, enough context to reuse it, useful reproduction/validation commands, and failed approaches when they would otherwise be tempting to repeat.

Do not hide human-relevant architecture exclusively in agent notes; promote it to human-facing docs too.

Tracked task workspaces are deliberately less permanent than `.agents/`. Put intermediate cross-task/context knowledge at the narrowest convenient shared task scope, read only workspace material relevant to the active task, and promote durable conclusions before its temporary scope is archived or retired. Consolidate or prune active workspace material when its size itself becomes a context burden.

## Git history preservation

Normal correction is additive: new corrective commits, reverts, fast-forward ref movement, and new branches/checkpoints.

Do not rewrite/discard existing reachable history or unique work without explicit human authorization identifying the affected history/ref and operation.

## Validation

Use real checks matching the changed surface. Documentation/policy changes may be validated by rereading, link/path checks, tree inspection, and consistency review. Add executable tests/checks as implementation appears; do not invent fake build commands before tooling exists.

## Provenance

Follow `../AGENTS.md` and [`PROVENANCE.md`](PROVENANCE.md). Resolve the authoring agent variant through the canonical registry before creating a wholly agent-authored substantive commit. If the variant is unnamed/unregistered, follow the `UNNAMED` notification/ask rules rather than inventing a designation.

## Initiatives

Initiatives are structured context, not executable work.

Consult an initiative when the active task/spec links it or when a newly discovered gap appears to be intentionally deferred structured work rather than a casual idea. Do not add initiatives to Dispatch, claim them, or infer authorization from them.

Use `autonomic_affairs/reminders.md` for lightweight "do not forget" ideas, `autonomic_affairs/initiatives/` for recognized multi-phase unfinished intent/debt, and `autonomic_affairs/agent_tasks.md` plus task specs for bounded executable work.
