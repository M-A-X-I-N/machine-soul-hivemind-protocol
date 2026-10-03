# Agent workflow and recovery conventions

## Checkpoint discipline

For repository-changing work:

1. inspect the active branch/current state;
2. read `../autonomic_affairs/tasks.md`, inspect Dispatch, and open the linked detailed task specification;
3. when claiming dispatched work, atomically change its index state to `IN_PROGRESS`, remove it from Dispatch, and add/update its row in **Active claims** with the authorized lineage and canonical branch;
4. keep each checkpoint narrow enough to explain and revert independently;
5. run the smallest validation that genuinely proves the changed surface;
6. commit/push meaningful completed work promptly;
7. when a task completes, set it to `COMPLETE`, remove its Active-claims row, then populate Dispatch with the next authorized/eligible work in priority order;
8. persist expensive reusable discoveries under `.agents/`.

Do not leave substantial completed work only in an ephemeral tool session.

## Task granularity default

Unless the human explicitly requests a particular task structure, agents have broad discretion to choose the task boundaries that function best for the agent actually executing the work. Optimize for coherent implementation, validation, dependency clarity, recoverability, and cross-context survivability. Do not prefer either tiny or large tasks for their own sake; Git/checkpoint overhead is one practical factor among those concerns.

The task system exists primarily to preserve executable intent and intermediate state across context/session boundaries, not to require ceremony for every repository edit.

If a change is isolated from any larger active block and is obviously one natural commit, no task is required. In that case inspect the relevant authority, make the change, validate the changed surface, and commit/push it directly.

Do not use this exception to bypass task state for work that is already part of an active task/block, has meaningful sequencing/dependencies, spans multiple checkpoints, or could plausibly be interrupted between distinct decisions.

### Terminal block archival

The active task surface contains non-terminal work only. Once every task in a block is terminal (`COMPLETE`, `CANCELLED`, or `SUPERSEDED`), move that block directory intact under `autonomic_affairs/tasks/archive/<block-id>/` and remove its rows from the active scheduling index. Preserve task IDs and block/task-scoped workspaces. Never archive a block that still contains a non-terminal task.

When the final task in a block performs the archival itself, release its Active claim and remove the block rows as part of the same terminal checkpoint so no terminal block remains falsely active.

## Agent lineages and working branches

Normal substantive development should occur in a recoverable agent lineage namespace unless a direct `main` change is naturally simpler.

A lineage identifier is `{name}_YYMMDD-HHmmss`: a four-letter lowercase ASCII female, neutral, or fantasy-style human-readable name plus its UTC creation timestamp. Prefer an initial not already in active/recent use when practical; do not maintain a canonical name registry.

The lineage owns `agent/{identifier}/*`; its canonical working branch is `agent/{identifier}/main`. It may create additional branches anywhere inside that namespace.

A transport/session interruption does not itself require a new lineage, but **lineage discovery is not recovery authority**. A different chat/agent may adopt an existing lineage only when either:

1. the human explicitly requests recovery/adoption of that specific lineage or branch; or
2. the current conversation already established ownership of that lineage and the human gives an unambiguous continuation/recovery instruction referring to that established work.

Merely finding an `agent/**` branch, an apparently abandoned task, an `IN_PROGRESS` state, or future claim metadata is never sufficient authority. An unrelated agent may inspect such state and may ask whether recovery is desired, but must not mutate the lineage or present itself as that lineage without authorization.

After authorized recovery, compare the actual lineage head/history with the expected checkpoint before writing. If unexpected unrelated work has appeared in the namespace, stop adoption and reconcile with the human instead of overwriting, merging through, or silently treating the foreign work as part of the recovered lineage.

Cross-agent coordination, task bookkeeping, and similarly natural repository-control changes may still land directly on `main`.

### Active task claims

`autonomic_affairs/tasks.md` contains an **Active claims** section separate from task tables. A claim is a live coordination lock saying which authorized lineage currently owns execution of a task.

Claim lifecycle:

- claiming normally means `QUEUED → IN_PROGRESS`, removal from Dispatch, and claim-row creation in the same checkpoint;
- `IN_PROGRESS`, `BLOCKED`, and `AWAITING_DEFERRED_CI` may retain their claim while that lineage still owns continuation;
- freezing active work normally releases its claim unless the human/agent explicitly records that the freeze retains exclusive ownership;
- `COMPLETE`, `CANCELLED`, and `SUPERSEDED` tasks must not keep active claims;
- explicit handoff changes the claim only after the receiving lineage is authorized under the recovery/adoption rules.

A claim is **never** authority to adopt that lineage. If a claim appears stale, inconsistent with task state, points at a missing/diverged branch, or conflicts with current conversation authority, inspect and reconcile it; do not silently delete it, steal it, or treat it as permission to recover.

Git history is the historical record of old claims. Remove released/completed claim rows instead of maintaining a second permanent claim archive.

## CI selection and deferred validation

CI is chosen for validation value while avoiding unnecessary runner provisioning.

- `.github/workflows/machine_soul_validation.yml` is the sole checked-in CI event entry point for pushes to `main`, PRs targeting `main`, manual dispatch, and the daily schedule.
- Automatic push/PR selection uses changed paths as **conservative evidence**, not unquestioned authority. Known relevance selects logical checks; unknown paths, missing/ambiguous Git evidence, or control-plane uncertainty fail safe to the complete registered check set.
- Check selection is finer-grained than runner provisioning. Compatible selected checks share the same Linux/Windows/fresh-clone runner job; an unrelated check must not run merely because another check needs that OS.
- A pushed/PR head may use one `CI:` line: `auto`, `all`, `none`, exact registered check IDs, or documented convenience groups such as `linux` / `windows`. Valid explicit intent overrides automatic path classification. Malformed/unknown selectors fail visibly while selecting every registered check.
- `CI:` covers both blocking checks and deferred CodeQL checks. CodeQL launch routing is centralized even though its lifecycle remains deferred.
- Native `skip-checks: true` remains the harder GitHub-level bypass when a push/PR should instantiate no checked-in workflow at all. GitHub requires the trailer section to be preceded by **two empty lines** and requires `skip-checks` to be the last trailer; preserve that spacing exactly.
- Ordinary non-main pushes, including `agent/**`, stay quiet. Manual validation can target a selected ref and uses explicit selection rather than inventing an automatic diff.
- The daily schedule is `9 6 * * *` (06:09 UTC) and reconciles missing coverage on default-branch HEAD. Ordinary checks may carry successful coverage across unrelated commits; CodeQL requires exact-HEAD success and runs every 24 hours while HEAD is younger than 168 hours, then every 168 hours.
- The selector validates repository commit/control metadata across the introduced push/PR commit range when evidence is available.

The current registered check IDs are `linux-python`, `linux-applications`, `linux-install`, `linux-session`, `linux-matrix`, `windows-python`, `windows-applications`, `windows-posix`, `windows-install`, `fresh-linux`, `fresh-windows`, `codeql-python`, and `codeql-actions`.

`AWAITING_DEFERRED_CI` means implementation and advancement-blocking CI are complete, but explicitly deferred repository analysis is still pending. Such a task may yield active work to the next task, but cannot become `COMPLETE` until required deferred checks succeed. Later tasks in the same ordered workstream must not be marked `COMPLETE` past an unresolved earlier deferred task. Substantive deferred-analysis failures reopen/block originating work; infrastructure-only failures are retried/investigated separately.

`FROZEN` is an intentional priority/policy hold. It is neither a dependency nor evidence of a technical blocker.

## Interrupted-session recovery

Recovery has two separate questions: **what happened?** and **who is authorized to continue a lineage?** Repository inspection answers the first; it does not answer the second.

Do not assume the last narrated action reached the repository. Inspect branch heads/history, compare `../autonomic_affairs/tasks.md` plus the relevant task specification with actual commits/files, and resolve a known task ID through `../autonomic_affairs/tasks/README.md` when it may already be archived. Distinguish committed work from orphaned/reasoning-only work and validate recovered state before continuing.

Inspecting an existing lineage for recovery evidence is always allowed. Mutating/adopting it requires the authority rules in **Agent lineages and working branches** above. If no such authority exists, ask whether the human wants that specific lineage recovered rather than recovering it automatically.

Even with recovery authority, stop if the branch contains unexpected unrelated commits relative to the expected checkpoint. Preserve those commits and resolve ownership/divergence explicitly; do not force-move or absorb them merely to resume the expected work.

Prefer recovering already-created correct Git objects over recreating them manually.

## Source-of-truth discipline

When information conflicts, prefer the source that owns the subject:

1. tracked configuration/source for implemented behavior;
2. human-facing architecture/policy docs for durable design;
3. `autonomic_affairs/tasks.md` for scheduling/state/Dispatch and `autonomic_affairs/tasks/` for active/archived execution specifications plus temporary task workspaces;
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

Use `autonomic_affairs/reminders.md` for lightweight "do not forget" ideas, `autonomic_affairs/initiatives/` for recognized multi-phase unfinished intent/debt, and `autonomic_affairs/tasks.md` plus task specs for bounded executable work.
