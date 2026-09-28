# Persisted agent context

This directory is a **living project memory for agents**.

It stores procedure, recovery guidance, navigation help, and durable technical discoveries useful across chats/tool sessions but too agent-oriented for root documentation.

Unlike some sibling repositories, this project explicitly encourages proactive retention of expensive-to-rediscover technical knowledge here.

## What belongs here

Good candidates include workflow/recovery conventions, host/platform/application quirks, exact config/install locations, symlink and privilege behavior, failed approaches and why they failed, diagnostics, architecture discoveries, verified assumptions, and source-of-truth/navigation guidance.

If meaningful effort was spent learning something and it is likely to matter again, preserve it.

## What does not belong here

- live task scheduling/state — use `../autonomic_affairs/agent_tasks.md`; active and archived execution specifications live under `../autonomic_affairs/agent_tasks/`;
- structured non-executable unfinished work/debt — use `../autonomic_affairs/initiatives/`;
- temporary task/block/workstream research needed mainly to carry unfinished work across context boundaries — use the relevant tracked task workspace under `../autonomic_affairs/agent_tasks/`;
- secrets, tokens, passwords, private keys, or other sensitive machine-local values;
- generated output or disposable scratch data;
- machine-local mutable deployment state — use ignored `../scratch/`;
- duplicated authoritative human-facing docs;
- unrelated personal/chat history.

## Organization

Prefer these categories when useful:

```text
.agents/
├── README.md
├── WORKFLOW.md
├── PROVENANCE.md
├── architecture/
├── applications/
├── hosts/
├── platforms/
├── investigations/
└── decisions/
```

Do not create empty taxonomy merely for appearance. Add subdirectories when there is actual knowledge to place there.

Prefer updating an existing note over creating a competing note on the same subject. Mark uncertainty and how knowledge was obtained.

## Fresh-session reading order

1. `../AGENTS.md`
2. `WORKFLOW.md`
3. `PROVENANCE.md` before authoring commits
4. `../autonomic_affairs/agent_tasks.md` and the linked specification for the dispatched/claimed active task; for historical/recovery lookup, resolve the task ID using `../autonomic_affairs/agent_tasks/README.md`
5. only task-workspace files explicitly relevant to the active work
6. relevant notes under this directory
7. relevant human-facing documentation/configuration

Current repository state remains authoritative over remembered conversation context.
