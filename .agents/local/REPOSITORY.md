# Machine-Soul repository policy

Read this file for substantial work in this repository.

This file contains MSHP-specific normative policy. It extends the generic baseline instructions under `.agents/baseline/`. Where this file explicitly conflicts with a baseline instruction, this local rule wins.

## Repository purpose

Machine-Soul Hivemind Protocol annexes machines into the Machine Soul across multiple hosts, platforms, users, shells, terminals, runtimes, tools, and applications.

Configuration is one managed capability, not the definition of support.

## Local source-of-truth map

- `autonomic_affairs/tasks.md` owns executable-work scheduling metadata, Dispatch, and Active claims.
- `autonomic_affairs/tasks/` owns task specifications, temporary task workspaces, and structured archived task material.
- `autonomic_affairs/reminders.md` owns deliberately non-executable lightweight future ideas.
- `autonomic_affairs/initiatives/` owns structured non-executable unfinished work/debt.
- `assimilation_directives/` owns canonical tracked desired configuration/behavioral content when such content exists.
- human-facing architecture/policy documentation owns durable project design.
- `.agents/local/` owns MSHP-specific normative agent policy.
- `.agents/memory/` owns durable non-normative agent knowledge whose rediscovery would be wasteful.
- task workspaces under `autonomic_affairs/tasks/` own tracked temporary/intermediate knowledge needed across task/context boundaries.
- `scratch/` is ignored machine-local mutable state.

Do not create competing task ledgers or duplicate authoritative policy.

## Local policy routing

Read additional local policy only when the work makes it relevant:

- adding, moving, or classifying repository material → `LAYOUT.md`;
- changing configuration deployment, Apply/Unapply/Check behavior, or related application-state safety → `CONFIGURATION.md`;
- changing or diagnosing CI/control-plane behavior → `CI.md`.

## MSHP engineering style

- Prefer native platform/application mechanisms over unnecessary bespoke machinery.
- Keep shared configuration-deployment runtime behavior separate from application-specific adapters.
- Keep host/account/platform special cases declarative where practical.
- Follow `autonomic_affairs/docs/DOCUMENTATION_STYLE.md` for durable documentation identity/role conventions and internal-humor boundaries.
- A fresh clone should eventually reconstruct behavior from repository state plus intentionally machine-local `scratch/` data.

## Task storage

MSHP uses the generic baseline task lifecycle.

Local physical storage:

- ledger: `autonomic_affairs/tasks.md`;
- active task specs/workspaces: `autonomic_affairs/tasks/<block-id>/`;
- terminal archives: `autonomic_affairs/tasks/archive/<block-id>/`;
- task lookup/storage rules: `autonomic_affairs/tasks/README.md`.

Task IDs remain stable when blocks archive.

## Reminders and initiatives

MSHP uses the baseline non-executable semantics.

Local storage:

- reminders: `autonomic_affairs/reminders.md`;
- initiatives: `autonomic_affairs/initiatives/`.

Neither location is Dispatch authority.
