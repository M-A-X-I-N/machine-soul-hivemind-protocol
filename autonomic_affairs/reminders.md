# Reminders

This file holds ideas that are intentionally **not yet executable agent tasks**.

A reminder:

- is not part of Dispatch;
- carries no authorization to act;
- must not be silently executed or promoted by an agent;
- becomes executable work only after discussion/refinement makes it sufficiently specified for `agent_tasks`.

Keep this register simple until real use demonstrates a need for additional structure.

## Cross-repository provenance normalization / gloriously unnecessary rebases

After the new agent-provenance policy has stabilized, audit the maintainer's other repositories for legacy `Agent-authored-by:` conventions and stable-designation references.

The long-term temptation is to normalize historical commit messages with fat, completely unnecessary rebases/history rewrites.

Before this reminder can become executable work:

- enumerate every affected repository;
- enumerate the exact branches/refs and history ranges;
- identify collaboration/clone/PR/link implications;
- determine the rewrite procedure and recovery plan;
- obtain explicit human authorization for each affected history/ref and destructive rewrite.

Merely recording this reminder does **not** authorize any rebase, force-push, ref rewrite, or history destruction.

## Standardize baseline agent infrastructure across repositories

Design and eventually implement a reusable baseline for agent-facing repository infrastructure across the maintainer's repositories.

Use Machine-Soul as the base/reference parent for generic conventions while allowing individual repositories to layer project-specific additions or overrides without unnecessarily copying/forking the shared baseline.

Areas worth considering include:

- root `AGENTS.md` conventions;
- `.agents/` structure and reading order;
- recovery/checkpoint workflow;
- provenance registry/policy;
- agent-task index/spec/archive format;
- documentation/style rules;
- future reusable Skills or equivalent workflows.

Before promotion to executable work, decide how the shared baseline is distributed/synchronized and how repository-local overrides remain explicit rather than being overwritten.

## Investigate OpenAI Skills for reusable repository workflows

Investigate whether repeatable Machine-Soul workflows are worth expressing as OpenAI Skills or related reusable agent workflows.

Candidate workflows include:

- interrupted-session recovery;
- claiming/executing an agent task;
- adding a new application integration;
- validating a checkpoint.

The investigation should distinguish:

- repository-local Skill discovery, especially Codex-oriented workflows;
- installed/shared Skills available through supported ChatGPT surfaces such as Chat and Work;
- actual portability of one Skill definition across those surfaces;
- what state/context a Skill can reliably discover from a repository;
- whether Skills materially improve this repository over concise `AGENTS.md` plus `.agents/` procedures.

Do not implement Skills merely because the mechanism exists.

Revisit this after the canonical task schema is established so any task-execution Skill can target the real `agent_tasks.md` contract rather than a transitional format.
