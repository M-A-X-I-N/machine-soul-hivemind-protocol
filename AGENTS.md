# Agent operating guide

This repository preserves and applies the Machine Soul across multiple hosts, platforms, users, shells, terminals, and applications.

Keep this file concise. Detailed agent procedure and persisted context live under [`.agents/`](.agents/). The authoritative executable-work ledger is [`autonomic_affairs/agent_tasks.md`](autonomic_affairs/agent_tasks.md).

## Before substantive work

1. Read this file.
2. Read [`.agents/README.md`](.agents/README.md) and [`.agents/WORKFLOW.md`](.agents/WORKFLOW.md).
3. Read [`autonomic_affairs/agent_tasks.md`](autonomic_affairs/agent_tasks.md), inspect **Dispatch**, and open the linked task specification before substantive work unless the human redirects work.
4. Inspect the current repository/branch state before assuming remembered chat state is current.
5. Read only the application/host/platform notes relevant to the active task.

Repository state and tracked durable documentation are authoritative over remembered conversation context.

## Source-of-truth ownership

- `autonomic_affairs/agent_tasks.md` owns executable-work scheduling metadata and Dispatch; linked files under `autonomic_affairs/agent_tasks/` own full task instructions.
- `autonomic_affairs/reminders.md` owns deliberately non-executable future ideas. Reminders are not authorization and must not be silently executed/promoted.
- Tracked configuration files own canonical desired configuration.
- Human-facing architecture/policy documentation owns durable project design.
- `.agents/` owns agent procedure plus durable, useful agent memory that would be wasteful to rediscover.
- `scratch/` is machine-local mutable state and is Git-ignored.

Do not create competing task ledgers.

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

## Git and checkpoint discipline

- Preserve Git history and recoverability by default.
- Prefer additive corrections and revert commits over history rewriting.
- Do not force-move refs, rebase/drop/squash established history, or destroy unique work without explicit human authorization for the affected history and operation.
- Keep checkpoints small, coherent, and independently understandable/revertible.
- Push meaningful completed checkpoints promptly.
- Use the smallest validation that genuinely proves the changed surface.
- If a task exposes a genuine architecture/design ambiguity that prevents safe progress, stop and ask rather than silently choosing for the human.
- Update `autonomic_affairs/agent_tasks.md` whenever executable-work state, dependencies, summaries, or Dispatch ordering changes.
- If a task discovers durable reusable knowledge, update `.agents/` in the same checkpoint or immediately after it.

## Commit messages and provenance

Use `[Kind][Scope] Imperative summary`. Scope is optional when it adds no useful information.

Approved kinds: `Feature`, `Fix`, `Research`, `Documentation`, `Test`, `CI`, `Build`, `Refactor`, `Chore`, and human-selected-only `CBA`. Agents must never self-select `CBA`.

Wholly agent-authored substantive commits must follow the canonical [agent provenance registry and trailer policy](.agents/PROVENANCE.md). Do not invent a stable designation when the authoring agent variant is unregistered or marked `UNNAMED`.

## Working style

- Prefer native platform/application mechanisms over unnecessary bespoke machinery.
- Keep shared configuration-deployment runtime behavior separate from application-specific adapters.
- Keep host/account/platform special cases declarative where practical.
- Follow [`autonomic_affairs/docs/DOCUMENTATION_STYLE.md`](autonomic_affairs/docs/DOCUMENTATION_STYLE.md): durable docs use generic machine/account roles unless a concrete identity is materially necessary.
- Do not invent ceremonial validation merely to claim a task was tested.
- A fresh clone should eventually reconstruct behavior from repository state plus intentionally machine-local `scratch/` data.
