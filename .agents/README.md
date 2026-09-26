# Persisted agent context

This directory is a **living project memory for agents**.

It stores procedure, recovery guidance, navigation help, and durable technical discoveries useful across chats/tool sessions but too agent-oriented for root documentation.

Unlike some sibling repositories, this project explicitly encourages proactive retention of expensive-to-rediscover technical knowledge here.

## What belongs here

Good candidates include workflow/recovery conventions, host/platform/application quirks, exact config/install locations, symlink and privilege behavior, failed approaches and why they failed, diagnostics, architecture discoveries, verified assumptions, and source-of-truth/navigation guidance.

If meaningful effort was spent learning something and it is likely to matter again, preserve it.

## What does not belong here

- the active global task list — use `../TASKS.md`;
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
3. `../TASKS.md`
4. relevant notes under this directory
5. relevant human-facing documentation/configuration

Current repository state remains authoritative over remembered conversation context.
