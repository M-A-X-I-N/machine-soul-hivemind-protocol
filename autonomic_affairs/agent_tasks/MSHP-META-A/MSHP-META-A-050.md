# MSHP-META-A-050 — Establish a non-executable reminders register

## Description

Create a durable register for ideas intentionally not refined/authorized enough to be executable agent tasks.

## Requirements

- Create `autonomic_affairs/reminders.md`.
- Document that reminders are not dispatched, do not imply authorization, and must not be silently executed.
- Require discussion/refinement before promotion into `agent_tasks`.
- Seed a reminder to audit other maintainer repositories for legacy provenance and, only after explicit repo/ref/history authorization, consider gloriously unnecessary history-rewriting/rebases to normalize it.
- Seed a reminder to design/implement a reusable baseline agent-file/convention structure across the maintainer's repositories, using Machine-Soul as the parent/reference while permitting project-specific extensions.
- Seed a reminder to investigate OpenAI Skills for reusable workflows such as recovery, task execution, adding applications, and checkpoint validation, distinguishing repo-local Codex discovery from installed/shared ChatGPT surfaces.

## Constraints / non-goals

- Do not execute any reminder during this task.
- Do not design a complex reminder ID/state system before actual usage demonstrates a need.
- Do not authorize history rewriting merely by recording the reminder.

## Acceptance criteria

- All three agreed reminders are durably recorded.
- The file clearly distinguishes reminders from executable/authorized tasks.
- Agents are explicitly prohibited from silently promoting/executing reminders.

## Validation

- Read the reminders file from a fresh-context perspective and confirm none can be mistaken for Dispatch.
- Verify agent/task documentation links to the reminder semantics where useful.
