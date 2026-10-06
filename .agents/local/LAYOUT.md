# Machine-Soul repository layout policy

Read this file when adding, moving, or classifying repository material, or when a thematic top-level path is otherwise ambiguous.

## Top-level directory contract

These thematic names are intentionally not self-explanatory. Treat this table as the binding placement contract.

| Domain | Belongs here | Does not belong here |
|---|---|---|
| `abandoned_artifacts/` | Superseded, deprecated, failed, recently decommissioned, or otherwise inactive material that may still contain useful history/fragments and is not ready to live only in Git history. | Current/authoritative implementation, ordinary backups, active experiments, or material with a narrower canonical archive. |
| `accumulated_instruments/` | Standalone reusable tools, utilities, diagnostics, converters, repair scripts, and small programs kept with this repository but not intrinsically part of annexation/assimilation. | Application lifecycle/configuration machinery, active prototypes, or knowledge-only notes. |
| `acquired_intelligence/` | Durable technical knowledge/references/discoveries useful beyond one active task/project decision. | Agent operating procedure, live task workspaces, canonical project architecture, executable tools, or machine-local scratch. |
| `annexation/` | Executable machinery that acquires, installs, discovers, reconciles, removes, or otherwise manages machine/application/runtime state as part of Machine-Soul. | Canonical desired configuration, unrelated tools, or unstable experiments. |
| `arcane_experiments/` | Tracked prototypes, proof-of-concepts, reverse-engineering attempts, temporary harnesses, and uncertain ideas still being tested. | Stable production machinery, durable conclusions, or ignored local scratch. |
| `assembled_assets/` | Inert/static reusable resources such as icons, wallpapers, images, templates, exported resources, configuration-adjacent static files, and reusable skeletons. | Executable code, learned knowledge, canonical behavioral configuration, or active experiments. |
| `assimilation/` | Canonical tracked desired behavior/configuration: how an assimilated target should behave. | Install/discovery/orchestration code, generic tools, or static assets merely consumed by directives. |
| `meta/` | Repository/project control plane: tasks, claims, Dispatch, reminders, initiatives, project docs/tests, CI-control helpers, and related governance. | Machine-targeted configuration, annexation code, generic standalone utilities, or unrelated reference knowledge. |
| `.agents/` | Agent instructions plus durable agent-facing memory according to its baseline/local/memory split. | Live scheduling state, task workspaces, canonical human architecture, secrets, or mutable machine-local state. |
| `.github/` | GitHub-defined repository automation/configuration whose path is externally dictated. | Generic scripts merely because CI calls them, project docs, or agent memory. |
| `scratch/` | Ignored machine-local mutable state: backups, deployment state, local env/secrets, temp files, logs, caches, and disposable local work. | Anything that must survive cloning or be repository truth. |

## Classification shortcuts

- still discovering what it is → `arcane_experiments/`;
- reusable standalone tool → `accumulated_instruments/`;
- enduring result is knowledge → `acquired_intelligence/` or the narrower authoritative docs/agent-memory location;
- inert/static consumed material → `assembled_assets/`;
- obsolete but still too valuable/recent for Git history alone → `abandoned_artifacts/`;
- machine-local and not clone-worthy → ignored `scratch/`.

Misclassification is recoverable. Silent deletion or duplicate competing authority is worse.
