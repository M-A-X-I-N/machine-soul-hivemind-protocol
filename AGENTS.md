# Agent operating guide

This repository annexes machines into the Machine Soul across multiple hosts, platforms, users, shells, terminals, runtimes, tools, and applications. Configuration is one managed capability, not the definition of support.

Keep this file concise. Detailed agent procedure and persisted context live under [`.agents/`](.agents/). The authoritative executable-work ledger is [`autonomic_affairs/agent_tasks.md`](autonomic_affairs/agent_tasks.md).

## Before substantive work

1. Read this file.
2. Read [`.agents/README.md`](.agents/README.md) and [`.agents/WORKFLOW.md`](.agents/WORKFLOW.md).
3. Read [`autonomic_affairs/agent_tasks.md`](autonomic_affairs/agent_tasks.md), inspect **Dispatch**, and open the linked task specification before substantive work unless the human redirects work.
4. Inspect the current repository/branch state before assuming remembered chat state is current.
5. Read only the application/host/platform notes relevant to the active task.

Repository state and tracked durable documentation are authoritative over remembered conversation context.

## Source-of-truth ownership

- `autonomic_affairs/agent_tasks.md` owns executable-work scheduling metadata, Dispatch, and the live **Active claims** coordination section; `autonomic_affairs/agent_tasks/` owns active task specifications, temporary task workspaces, and structured archived task material. Task IDs remain stable even when completed blocks move into `agent_tasks/archive/`.
- `autonomic_affairs/reminders.md` owns deliberately non-executable future ideas. Reminders are not authorization and must not be silently executed/promoted.
- `autonomic_affairs/initiatives/` owns structured, intentionally unfinished work/debt that is more concrete than a reminder but is still non-executable. Initiatives are context, never Dispatch authorization.
- `assimilation_directives/` owns canonical tracked desired configuration/behavioral content when such content exists. A supported annexation target does not need an assimilation directive.
- Human-facing architecture/policy documentation owns durable project design.
- `.agents/` owns agent procedure plus durable, useful agent memory that would be wasteful to rediscover.
- Task workspaces under `autonomic_affairs/agent_tasks/` own tracked temporary/intermediate knowledge needed across task or context boundaries; they are not permanent agent memory and are not mandatory reading unless relevant.
- `scratch/` is machine-local mutable state and is Git-ignored.

Do not create competing task ledgers.

## Top-level directory contract

These names are deliberately thematic and are therefore **not self-explanatory**. Treat this table as the binding placement contract for new repository material.

| Domain | Belongs here | Does **not** belong here |
|---|---|---|
| `abandoned_artifacts/` | Superseded, deprecated, failed, recently decommissioned, or otherwise inactive material that may still contain useful history/fragments and is not yet ready to live only in Git history. | Current/authoritative implementation, ordinary backups, active experiments, or canonical archives that already have a defined home. |
| `accumulated_instruments/` | Standalone reusable tools, utilities, diagnostics, converters, repair scripts, and small programs worth keeping with this repository but not intrinsically part of Machine-Soul annexation/assimilation. | Application lifecycle/configuration machinery, active prototypes, or knowledge-only notes. |
| `acquired_intelligence/` | Durable technical knowledge, references, discoveries, platform/application behavior, expensive-to-rediscover facts, and scar tissue that are useful beyond one active task/project decision. | Agent operating procedure, live task workspaces, canonical project architecture, executable tools, or machine-local scratch data. |
| `annexation_procedures/` | Executable machinery that acquires, installs, discovers, reconciles, removes, or otherwise manages machine/application/runtime state as part of Machine-Soul. | Canonical desired configuration content, unrelated standalone utilities, or experimental scratch that has not earned production status. |
| `arcane_experiments/` | **Tracked** prototypes, proof-of-concepts, reverse-engineering attempts, temporary harnesses, and uncertain ideas still being tested before promotion. | Stable production machinery, durable knowledge after conclusions are known, or ignored machine-local scratch state. |
| `assembled_assets/` | Inert or primarily static reusable resources: icons, wallpapers, images, templates, exported visual resources, configuration-adjacent static files, redistributable font-related material, and reusable skeletons. | Executable code, learned knowledge, canonical behavioral configuration, or active experiments. |
| `assimilation_directives/` | Canonical tracked desired behavior/configuration that answers **how an assimilated machine/application should behave**. | Install/discovery/orchestration code, generic tools, or static assets that are merely consumed by directives. |
| `autonomic_affairs/` | Repository/project self-management and control-plane material: tasks/claims/Dispatch, reminders, initiatives, project docs, repository tests, CI-control helpers, and related governance. | Machine-targeted application configuration, machine annexation code, generic standalone utilities, or unrelated reference knowledge. |
| `.agents/` | Required agent procedure plus durable agent-facing memory whose rediscovery would be wasteful: workflow/recovery guidance, verified quirks, investigations, decisions, and navigation help. | Live scheduling/claims, temporary task workspace material, human-facing canonical architecture, secrets, or machine-local mutable state. |
| `.github/` | GitHub-defined repository automation/configuration such as Actions workflows and other GitHub platform files whose location is externally dictated. | General scripts merely because CI happens to call them, project docs, or agent memory. |
| `scratch/` | **Ignored, machine-local mutable state**: backups, deployment state, local env/secrets, temporary files, logs, caches, and disposable local work. | Anything that must survive cloning, anything relied upon as repository truth, or tracked experiments intended to survive context/machine loss. |

Classification shortcuts:

- if it is still being poked to discover what it is, prefer `arcane_experiments/`;
- if it became a reusable standalone tool, promote it to `accumulated_instruments/`;
- if the enduring result is knowledge rather than code, promote it to `acquired_intelligence/` or the narrower authoritative docs/agent-memory location when applicable;
- if it is static material consumed by something else, prefer `assembled_assets/`;
- if it is obsolete but still too valuable/recent to discard into Git history alone, use `abandoned_artifacts/`;
- if it is machine-local and need not survive a clone, use ignored `scratch/` rather than any tracked domain.

Misclassification is recoverable. Silent deletion or duplicated competing authority is worse.

## Knowledge retention policy

Agents are explicitly **encouraged to add or update files under `.agents/` without asking permission first** when useful knowledge has meaningful rediscovery cost.

A good rule:

> If meaningful tool calls, investigation, experiments, or tokens were spent learning something likely to matter again, preserve it.

Examples include platform or application quirks, exact configuration locations, package/install behavior, symlink behavior and edge cases, host-specific facts, useful commands/diagnostics, failed approaches and why they failed, architecture discoveries, verified assumptions, recovery procedures, and external-tool limitations.

Record uncertainty honestly. Update existing notes rather than creating contradictory duplicates when practical.

Do **not** put secrets, private keys, tokens, passwords, or unrelated personal/chat history in `.agents/`.

Durable human-relevant project facts should also be promoted to the appropriate human-facing documentation rather than existing only in agent memory.

## Configuration safety laws

Unless the human explicitly changes these laws:

- canonical configuration lives in tracked repository **files**;
- application configuration is applied using **file-level symbolic links** into those tracked files;
- normal application does not copy configuration out of the repository;
- `$MACHINE_SOUL` identifies the canonical repository root;
- machine-local mutable data belongs under ignored `$MACHINE_SOUL/scratch/`;
- if Apply encounters an unmanaged existing destination, it must not destroy it silently;
- accepted replacement preserves prior state under `scratch/`;
- Apply is transactional where practical: validate → preserve → link → verify → record;
- Unapply removes only understood managed state and restores displaced state when safe;
- unexpected external changes cause a conflict rather than blind overwrite;
- Check reports meaningful state rather than only true/false;
- installing an application and applying its configuration are separate operations.

## Agent working branches and CI

- Prefer normal substantive development under `agent/{identifier}/main`, where `identifier` follows the repository lineage policy in [`.agents/WORKFLOW.md`](.agents/WORKFLOW.md). A lineage owns its entire `agent/{identifier}/*` namespace. **Discovering that namespace is never authority to adopt it.** Recovery adoption requires explicit human authorization identifying that lineage/branch, or an unambiguous current-conversation reference to lineage ownership already established in that conversation.
- Direct `main` changes remain valid when they naturally belong there, especially coordination/bookkeeping.
- Main integration defaults to full blocking CI; deliberate subset/no-CI behavior must be explicit. Non-main branches are quiet by default and may be validated explicitly when useful.
- CI selection is explicit intent, never changed-path inference. Optimize against wasted validation, not CI usage itself.

## Git and checkpoint discipline

- Preserve Git history and recoverability by default.
- Prefer additive corrections and revert commits over history rewriting.
- Do not force-move refs, rebase/drop/squash established history, or destroy unique work without explicit human authorization for the affected history and operation.
- Keep checkpoints coherent and independently understandable/revertible. When task structure is left to the agent, choose boundaries that best serve implementation, validation, recoverability, dependency clarity, and cross-context survival. Task or commit size is not itself a goal; do not split or combine work merely to make units smaller or larger.
- Push meaningful completed checkpoints promptly.
- Use the smallest validation that genuinely proves the changed surface.
- If a task exposes a genuine architecture/design ambiguity that prevents safe progress, stop and ask rather than silently choosing for the human.
- Update `autonomic_affairs/agent_tasks.md` whenever executable-work state, dependencies, summaries, or Dispatch ordering changes.
- Do not manufacture a task for an isolated repository change that is obviously one natural commit and is not part of a larger work block; perform, validate, and commit it directly. Tasks primarily exist to preserve executable intent across context/session boundaries.
- If a task discovers durable reusable knowledge, update `.agents/` in the same checkpoint or immediately after it.

## Commit messages and provenance

Use `[Kind][Scope] Imperative summary`. Scope is optional when it adds no useful information.

Approved kinds: `Feature`, `Fix`, `Research`, `Documentation`, `Test`, `CI`, `Build`, `Refactor`, `Chore`, and human-selected-only `CBA`. Agents must never self-select `CBA`.

Wholly agent-authored substantive commits must follow the canonical [agent provenance registry and trailer policy](.agents/PROVENANCE.md). Keep `Agent-authored-by:` even when Git Author is an agent/bot/service identity; in that case also use `Agent-operated-by:` when required by the provenance policy to identify the accountable human operator. Do not invent a stable designation when the authoring agent variant is unregistered or marked `UNNAMED`.

## Working style

- Prefer native platform/application mechanisms over unnecessary bespoke machinery.
- Keep shared configuration-deployment runtime behavior separate from application-specific adapters.
- Keep host/account/platform special cases declarative where practical.
- Follow [`autonomic_affairs/docs/DOCUMENTATION_STYLE.md`](autonomic_affairs/docs/DOCUMENTATION_STYLE.md): durable docs use generic machine/account roles unless a concrete identity is materially necessary.
- That style policy also permits optional maintainer-directed idiot-human humor internally; never apply it to end users or formal/user-facing interfaces.
- Do not invent ceremonial validation merely to claim a task was tested.
- A fresh clone should eventually reconstruct behavior from repository state plus intentionally machine-local `scratch/` data.
