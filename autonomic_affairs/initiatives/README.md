# Initiatives

This directory holds **structured, intentionally unfinished work or technical debt that is not itself executable agent work**.

Initiatives exist between casual reminders and executable tasks:

```text
reminder
    ↓ deliberate promotion
initiative
    ↓ bounded promotion
agent task(s)
```

## What an initiative means

An initiative records a real project concern whose desired end state, known gaps, or phases are concrete enough to preserve structurally, while some or all of that work is not currently useful or sufficiently specified to execute.

An initiative:

- is **not** part of Dispatch;
- does **not** authorize implementation;
- is never claimed or marked `IN_PROGRESS`;
- may remain `OPEN` while every currently useful executable task is complete;
- may contain known gaps that intentionally have no task;
- may link executable tasks without duplicating their mutable state/dependencies.

Use initiatives to prevent intentional gaps from becoming either zombie tasks or forgotten reminder prose.

## Lifecycle

Use only:

- `OPEN` — the recognized desired state still has material intentional gaps;
- `COMPLETE` — the initiative's closure criteria are satisfied;
- `ABANDONED` — the desired state is no longer pursued.

Status lives in the initiative file itself because initiatives are not a scheduling system.

Completed/abandoned initiatives normally remain in this directory for discoverability. If accumulation becomes materially noisy, they may move intact under `initiatives/archive/`; do not create an archive layer merely for symmetry.

## Required shape

Each initiative should contain:

- **Status**
- **Goal**
- **Current state / coverage**
- **Known gaps**
- **Deliberate boundaries / deferred work**
- **Related executable tasks**
- **Promotion / closure criteria**

Keep this lighter than task specs. Do not add Dispatch, task-style dependencies, blockers, or per-gap task requirements.

## Choosing the right surface

Use [`../reminders.md`](../reminders.md) when the thought is essentially:

> Do not forget this idea.

Use an initiative when the thought is:

> This is recognized unfinished project intent/debt with enough known structure that future agents should understand what is deliberately incomplete.

Use [`../tasks.md`](../tasks.md) and task specs when the thought is:

> This bounded work is sufficiently specified and authorized for execution through Dispatch.

A reminder does not become an initiative automatically. An initiative does not become executable automatically. Promotion is deliberate and should preserve the original intent rather than silently broadening scope.

## Reading behavior

Do not ingest every initiative during routine startup. Active task specs and durable architecture should point to relevant initiatives when their known gaps/boundaries matter.
