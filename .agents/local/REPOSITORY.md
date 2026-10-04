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

## Top-level directory contract

These thematic names are intentionally not self-explanatory. Treat this table as the binding placement contract.

| Domain | Belongs here | Does not belong here |
|---|---|---|
| `abandoned_artifacts/` | Superseded, deprecated, failed, recently decommissioned, or otherwise inactive material that may still contain useful history/fragments and is not ready to live only in Git history. | Current/authoritative implementation, ordinary backups, active experiments, or material with a narrower canonical archive. |
| `accumulated_instruments/` | Standalone reusable tools, utilities, diagnostics, converters, repair scripts, and small programs kept with this repository but not intrinsically part of annexation/assimilation. | Application lifecycle/configuration machinery, active prototypes, or knowledge-only notes. |
| `acquired_intelligence/` | Durable technical knowledge/references/discoveries useful beyond one active task/project decision. | Agent operating procedure, live task workspaces, canonical project architecture, executable tools, or machine-local scratch. |
| `annexation_procedures/` | Executable machinery that acquires, installs, discovers, reconciles, removes, or otherwise manages machine/application/runtime state as part of Machine-Soul. | Canonical desired configuration, unrelated tools, or unstable experiments. |
| `arcane_experiments/` | Tracked prototypes, proof-of-concepts, reverse-engineering attempts, temporary harnesses, and uncertain ideas still being tested. | Stable production machinery, durable conclusions, or ignored local scratch. |
| `assembled_assets/` | Inert/static reusable resources such as icons, wallpapers, images, templates, exported resources, configuration-adjacent static files, and reusable skeletons. | Executable code, learned knowledge, canonical behavioral configuration, or active experiments. |
| `assimilation_directives/` | Canonical tracked desired behavior/configuration: how an assimilated target should behave. | Install/discovery/orchestration code, generic tools, or static assets merely consumed by directives. |
| `autonomic_affairs/` | Repository/project control plane: tasks, claims, Dispatch, reminders, initiatives, project docs/tests, CI-control helpers, and related governance. | Machine-targeted configuration, annexation code, generic standalone utilities, or unrelated reference knowledge. |
| `.agents/` | Agent instructions plus durable agent-facing memory according to its baseline/local/memory split. | Live scheduling state, task workspaces, canonical human architecture, secrets, or mutable machine-local state. |
| `.github/` | GitHub-defined repository automation/configuration whose path is externally dictated. | Generic scripts merely because CI calls them, project docs, or agent memory. |
| `scratch/` | Ignored machine-local mutable state: backups, deployment state, local env/secrets, temp files, logs, caches, and disposable local work. | Anything that must survive cloning or be repository truth. |

Classification shortcuts:

- still discovering what it is → `arcane_experiments/`;
- reusable standalone tool → `accumulated_instruments/`;
- enduring result is knowledge → `acquired_intelligence/` or the narrower authoritative docs/agent-memory location;
- inert/static consumed material → `assembled_assets/`;
- obsolete but still too valuable/recent for Git history alone → `abandoned_artifacts/`;
- machine-local and not clone-worthy → ignored `scratch/`.

Misclassification is recoverable. Silent deletion or duplicate competing authority is worse.

## Configuration safety laws

Unless the human explicitly changes these laws:

- canonical configuration lives in tracked repository files;
- application configuration is applied using file-level symbolic links into those tracked files;
- normal application does not copy configuration out of the repository;
- `$MACHINE_SOUL` identifies the canonical repository root;
- mutable machine-local data belongs under ignored `$MACHINE_SOUL/scratch/`;
- unmanaged existing destinations are never destroyed silently;
- accepted replacement preserves prior state under `scratch/`;
- Apply is transactional where practical: validate → preserve → link → verify → record;
- Unapply removes only understood managed state and restores displaced state when safe;
- unexpected external changes produce conflict rather than blind overwrite;
- Check reports meaningful state rather than only true/false;
- installing an application and applying its configuration are separate operations.

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
