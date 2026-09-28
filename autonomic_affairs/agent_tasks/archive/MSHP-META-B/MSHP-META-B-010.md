# MSHP-META-B-010 — Establish initiative layer

## Description

Add a lightweight repository concept for structured, intentionally unfinished work that is too concrete for `reminders.md` but not itself executable agent work.

The initiative layer sits between casual reminders and executable `agent_tasks`.

Its first real use is the installation-scope effort: Machine-Soul should be able to implement a correct Windows/core scope model while explicitly retaining future Linux/package-manager gaps without keeping implementation tasks permanently incomplete or burying structured debt in a casual reminder.

## Requirements

- Add a tracked initiative area under `autonomic_affairs/` with concise agent/human-readable navigation and lifecycle rules.
- Define initiatives as **non-executable** structured work/debt:
  - they are not Dispatch entries;
  - they do not authorize implementation;
  - they may remain open while all currently useful executable tasks are complete;
  - they may contain known gaps that intentionally have no executable task yet.
- Keep initiative process lighter than the task system.
- Use only a minimal initiative lifecycle, preferably `OPEN`, `COMPLETE`, and `ABANDONED` unless implementation proves another state genuinely necessary.
- Define a small required initiative shape covering at least:
  - goal;
  - current state/coverage;
  - known gaps;
  - deliberate boundaries/deferred work;
  - related executable tasks;
  - promotion/closure criteria.
- Do **not** add Dispatch, task-style dependencies, IN_PROGRESS semantics, or per-gap task requirements to initiatives.
- Define the semantic distinction between:
  - `reminders.md` — "do not forget this idea";
  - initiatives — "recognized structured unfinished intent/debt";
  - `agent_tasks` — bounded executable work currently authorized through Dispatch.
- Define how a reminder may later be promoted into an initiative and how initiative portions become executable tasks without requiring the whole initiative to become executable.
- Define how completed/abandoned initiatives should be retained or archived without creating a second heavyweight task archive.
- Update the relevant task/agent workflow documentation so future agents know when to consult initiatives and do not mistake them for authorization.
- Create the first initiative for installation scope, using a stable human-readable identity such as `MSHP-INST-SCOPE`.
- Seed that initiative with the already-known problem:
  - target account, execution identity, installation scope, and ownership are distinct;
  - Windows/core scope work should proceed first;
  - future package-manager-specific Linux/user-scope support may remain intentionally incomplete;
  - installation takeover remains a separate concern/reminder unless later promoted explicitly.
- Keep existing reminders in place unless one must move to make the new distinction coherent; do not mass-promote reminders merely because initiatives now exist.

## Constraints / non-goals

- Do not turn initiatives into another scheduling index.
- Do not duplicate task lifecycle metadata inside initiative files.
- Do not require every initiative gap to have a task.
- Do not make all agents read every initiative at startup; task specs and relevant architecture should point to initiatives when they matter.
- Do not implement installation scope in this task.
- Do not implement or promote Windhawk, installation takeover, or unrelated reminders.
- Do not create speculative initiative taxonomy beyond demonstrated needs.

## Acceptance criteria

- The repository has a documented lightweight initiative layer with a clear boundary from reminders and executable tasks.
- Initiative files are explicitly non-executable and cannot be mistaken for Dispatch authorization.
- The first installation-scope initiative exists and can remain open even if Windows/core scope work completes before every future Linux/package-manager variant is supported.
- Future agents can tell where to record a newly discovered structured-but-deferred gap.
- Existing task/workspace/archive semantics remain intact and non-duplicative.

## Validation

- Walk examples for:
  - a casual idea that stays a reminder;
  - a structured multi-phase concern that becomes an initiative;
  - one bounded portion promoted into executable tasks;
  - an initiative remaining OPEN after all current tasks complete;
  - initiative completion/abandonment without task-history loss.
- Verify initiative documentation contains no executable/Dispatch semantics.
- Verify the installation-scope initiative links the `MSHP-INST-A` work without duplicating mutable task state.
- Review root/task/agent workflow documentation for contradictory source-of-truth claims.
