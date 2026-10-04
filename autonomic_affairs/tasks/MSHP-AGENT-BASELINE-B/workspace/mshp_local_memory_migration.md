
# MSHP-AGENT-BASELINE-B-030 — MSHP local/memory migration map

## Local normative instruction set

Candidate live local policy:

~~~text
.agents/local/
├── REPOSITORY.md
└── CI.md
~~~

No mirrored `local/WORKFLOW.md`, `local/GIT.md`, `local/PROVENANCE.md`, or `local/KNOWLEDGE.md` is justified today.

MSHP follows those baseline rules except where `REPOSITORY.md` or `CI.md` explicitly says otherwise.

## Explicit override model

Local policy changes baseline behavior only through an explicit normative statement.

Example shape:

> **Overrides baseline X:** <MSHP-specific rule and reason>.

No current MSHP local rule needs to disable the baseline task/lineage/history/provenance model wholesale.

Most MSHP specificity is additive: physical task paths, thematic directory ownership, configuration safety laws, and CI implementation.

## Current top-level instruction files

| Current file | B-040 destination | Classification |
|---|---|---|
| `AGENTS.md` | rewritten in place | thin entry/router + tiny MSHP orientation |
| `.agents/README.md` | rewritten in place | instruction/memory router |
| `.agents/WORKFLOW.md` | removed after `.agents/baseline/WORKFLOW.md` becomes authoritative | old mixed generic/local instruction |
| `.agents/PROVENANCE.md` | removed after `.agents/baseline/PROVENANCE.md` becomes authoritative | old generic instruction |
| `.agents/DEVELOPER_ANNEXATION.md` | `.agents/memory/architecture/developer_annexation.md` | durable MSHP implementation/roadmap memory |
| `.agents/GITHUB_ACTIONS_CONTROL.md` | `.agents/memory/decisions/github_actions_control.md` | CI experiment/history/rationale after current normative CI rules move to `local/CI.md` |
| `.agents/scrcpy_virtual_screen_manager.md` | `.agents/memory/tools/scrcpy_virtual_screen_manager.md` | tool-specific scar tissue |

## Existing category moves

All current files in these categories are non-normative knowledge and move intact unless path/link repairs are required:

~~~text
.agents/architecture/*     -> .agents/memory/architecture/*
.agents/decisions/*        -> .agents/memory/decisions/*
.agents/investigations/*   -> .agents/memory/investigations/*
.agents/platforms/*        -> .agents/memory/platforms/*
~~~

No content becomes normative merely because it mentions a past policy or decision.

Current normative policy lives only in root/router, `baseline/`, and `local/`.

## Complete current-file classification

### Memory / architecture

- `architecture/atomic_wrappers.md`
- `architecture/declarative_applications.md`
- `architecture/interactive_orchestration.md`
- `architecture/legacy_runtime_migration.md`
- `architecture/native_primitives.md`
- `architecture/operation_architecture.md`
- `architecture/operation_results.md`
- `architecture/python_core_implementation.md`
- `architecture/python_runtime.md`
- `architecture/scoped_installation_lifecycle.md`
- top-level `DEVELOPER_ANNEXATION.md` -> `memory/architecture/developer_annexation.md`

### Memory / decisions

- `decisions/developer_annexation_roadmap.md`
- `decisions/discovery_implementation_shape.md`
- `decisions/discovery_semantics.md`
- `decisions/git_history_attitude.md`
- `decisions/installation_scope_implementation_shape.md`
- `decisions/installation_scope_semantics.md`
- `decisions/main_active_iteration.md`
- `decisions/paired_taxonomy.md`
- `decisions/python_declarative_runtime.md`
- `decisions/python_migration_complete.md`
- `decisions/runtime_environment_discovery.md`
- `decisions/v2_stable_baseline.md`
- top-level `GITHUB_ACTIONS_CONTROL.md` -> `memory/decisions/github_actions_control.md`

### Memory / investigations

- `investigations/additional_runtime_candidates_2026-09.md`
- `investigations/agent_convention_survey.md`
- `investigations/effective_configuration_2026-09.md`
- `investigations/install_mechanisms_2026-09.md`
- `investigations/jetbrains_annexation_2026-09.md`
- `investigations/lua_multiversion_2026-09.md`
- `investigations/luarocks_annexation_2026-09.md`
- `investigations/node_multiversion_2026-09.md`
- `investigations/npm_annexation_2026-09.md`
- `investigations/package_environment_synthesis_2026-09.md`
- `investigations/pip_annexation_2026-09.md`
- `investigations/python_multiversion_2026-09.md`
- `investigations/runtime_synthesis_2026-09.md`
- `investigations/vscode_annexation_2026-09.md`
- `investigations/windows_config_candidates_2026-09.md`
- `investigations/windows_native_toolchain_annexation_2026-09.md`

### Memory / platforms

- `platforms/linux_installation_scope.md`
- `platforms/symlink_runtime_notes.md`
- `platforms/windows_installation_scope.md`
- `platforms/windows_posix_shell_adapter.md`

### Memory / tools

- top-level `scrcpy_virtual_screen_manager.md` -> `memory/tools/scrcpy_virtual_screen_manager.md`

## Human-facing documentation

Human-facing project architecture/policy under `autonomic_affairs/docs/` remains where it is.

The instruction refactor does not move it into agent memory.

Instruction files should point to human docs when durable project design is needed.

## Task/reminder/initiative state

These remain in place during B-040:

- `autonomic_affairs/tasks.md`;
- `autonomic_affairs/tasks/`;
- `autonomic_affairs/reminders.md`;
- `autonomic_affairs/initiatives/`.

Only instruction references to those locations change.

Their actual project state/history is repository-local state, not baseline instruction content.

## Link/reference migration requirements

B-040 must update live references to:

- `.agents/WORKFLOW.md` -> `.agents/baseline/WORKFLOW.md`;
- `.agents/PROVENANCE.md` -> `.agents/baseline/PROVENANCE.md`;
- `.agents/architecture/...` -> `.agents/memory/architecture/...`;
- `.agents/decisions/...` -> `.agents/memory/decisions/...`;
- `.agents/investigations/...` -> `.agents/memory/investigations/...`;
- `.agents/platforms/...` -> `.agents/memory/platforms/...`;
- top-level developer-annexation/action-control/scrcpy notes -> their new memory locations.

Relative links *inside moved memory files* require special validation because each file gains one additional path segment under `memory/`.

Do not assume blob-for-blob moves preserve relative links.

## Memory discoverability

The new `.agents/README.md` router should describe memory categories currently present but must not enumerate every file.

Relevant task specs/human docs/local policy should link directly to important memory when a task requires it.

Agents should search/browse `.agents/memory/` on demand rather than preload it.

## B-030 conclusion

MSHP needs only **two local normative files** for v1:

- `local/REPOSITORY.md`;
- `local/CI.md`.

Everything else currently under the old architecture is either:

- generic baseline instruction;
- non-normative memory;
- human-facing documentation;
- executable task/state material.

That gives B-040 a one-checkpoint migration target with no mixed-authority compatibility shims.
