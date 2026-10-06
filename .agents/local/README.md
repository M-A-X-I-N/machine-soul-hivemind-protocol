# Machine-Soul local instruction router

This file is repository-owned. It indexes MSHP-specific normative instructions, executable-work locations, and local memory organization.

Adding a repository-specific instruction file does **not** require a matching baseline file. Register the new file and its read trigger here; do not modify the baseline router merely to make the local file discoverable.

## Always for substantial MSHP work

Read [`REPOSITORY.md`](REPOSITORY.md).

It owns the high-frequency MSHP repository identity, source-of-truth map, engineering style, and local task/reminder/initiative locations.

## Subject-triggered local policy

| Situation | Read |
|---|---|
| adding, moving, or classifying repository material | [`LAYOUT.md`](LAYOUT.md) |
| configuration deployment, Apply/Unapply/Check behavior, installation/configuration ownership, or related state safety | [`CONFIGURATION.md`](CONFIGURATION.md) |
| CI/control-plane changes, CI selection/override, or deferred-validation diagnosis | [`CI.md`](CI.md) |

If a new local instruction file is introduced later, add its trigger to this table or another clearly named section in this file.

## Executable-work locations

- ledger / Dispatch / Active claims: [`../../meta/tasks.md`](../../meta/tasks.md);
- active task specifications/workspaces: [`../../meta/tasks/`](../../meta/tasks/);
- terminal task archive: [`../../meta/tasks/archive/`](../../meta/tasks/archive/);
- task storage/lookup rules: [`../../meta/tasks/README.md`](../../meta/tasks/README.md);
- reminders: [`../../meta/reminders.md`](../../meta/reminders.md);
- initiatives: [`../../meta/initiatives/`](../../meta/initiatives/).

## Local memory organization

Current useful non-normative memory categories under `../memory/` are:

- `architecture/`;
- `decisions/`;
- `investigations/`;
- `platforms/`;
- `tools/`.

Do not preload them. Dated investigations, migration records, and historical decision snapshots are on-demand references.

Do not create empty taxonomy for appearance. Add categories only when useful knowledge actually needs them.
