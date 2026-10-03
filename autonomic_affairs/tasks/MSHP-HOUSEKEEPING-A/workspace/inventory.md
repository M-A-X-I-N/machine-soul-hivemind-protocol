# MSHP-HOUSEKEEPING-A — Initial repository inventory

Captured for MSHP-HOUSEKEEPING-A-010 before archival or cleanup.

## Task boundary

HOUSEKEEPING-A is the only executable workstream.

Pre-existing non-terminal work outside HOUSEKEEPING-A:

- MSHP-WINGET-A-010 — FROZEN
- MSHP-WINGET-A-020 — FROZEN

No other pre-existing task is QUEUED, IN_PROGRESS, BLOCKED, or AWAITING_DEFERRED_CI.

Pre-existing terminal blocks still on the active task surface and therefore archival candidates:

- MSHP-DEV-A
- MSHP-DEV-B
- MSHP-OPS-A
- MSHP-OPS-B
- MSHP-APPS-A
- MSHP-OPS-C
- MSHP-OPS-D

Existing archived blocks: MSHP-META-A, MSHP-META-B, MSHP-INST-A, MSHP-INST-B, MSHP-DISC-A, MSHP-DISC-B, and legacy V2.

HOUSEKEEPING-A remains active until A-060, which owns its self-archive.

## Reminders

Current reminder headings:

1. Cross-repository provenance normalization / gloriously unnecessary rebases
2. Standardize baseline agent infrastructure across repositories
3. Investigate OpenAI Skills for reusable repository workflows
4. Agent-facing repository memory hygiene
5. Installation takeover
6. Windhawk configuration / mod-state management
7. Human review of agent instruction Markdown
8. Git history attitude and commit-history cleanup
9. Non-symlink configuration deployment strategy
10. Implement nuanced Git/commit-history cleanup policy
11. GitHub social preview artwork

The intended next discussion after HOUSEKEEPING-A is Standardize baseline agent infrastructure across repositories. It remains a reminder and is not executable housekeeping work.

## Initiatives

All current initiatives are intentionally non-executable and OPEN:

- MSHP-DEV-ENV — Developer environment annexation
- MSHP-INST-SCOPE — Installation scope
- MSHP-WIN-CONFIG — Additional Windows configuration surfaces

## Agent memory and instruction surface

Mandatory/governance entry points:

- AGENTS.md
- .agents/README.md
- .agents/WORKFLOW.md
- .agents/PROVENANCE.md
- autonomic_affairs/tasks.md
- autonomic_affairs/tasks/README.md
- autonomic_affairs/tasks/archive/README.md
- autonomic_affairs/reminders.md
- autonomic_affairs/initiatives/README.md

Tracked .agents files to review in A-050:

- .agents/DEVELOPER_ANNEXATION.md
- .agents/GITHUB_ACTIONS_CONTROL.md
- .agents/PROVENANCE.md
- .agents/README.md
- .agents/WORKFLOW.md
- .agents/architecture/atomic_wrappers.md
- .agents/architecture/declarative_applications.md
- .agents/architecture/interactive_orchestration.md
- .agents/architecture/legacy_runtime_migration.md
- .agents/architecture/native_primitives.md
- .agents/architecture/operation_architecture.md
- .agents/architecture/operation_results.md
- .agents/architecture/python_core_implementation.md
- .agents/architecture/python_runtime.md
- .agents/architecture/scoped_installation_lifecycle.md
- .agents/decisions/developer_annexation_roadmap.md
- .agents/decisions/discovery_implementation_shape.md
- .agents/decisions/discovery_semantics.md
- .agents/decisions/git_history_attitude.md
- .agents/decisions/installation_scope_implementation_shape.md
- .agents/decisions/installation_scope_semantics.md
- .agents/decisions/main_active_iteration.md
- .agents/decisions/paired_taxonomy.md
- .agents/decisions/python_declarative_runtime.md
- .agents/decisions/python_migration_complete.md
- .agents/decisions/runtime_environment_discovery.md
- .agents/decisions/v2_stable_baseline.md
- .agents/investigations/additional_runtime_candidates_2026-09.md
- .agents/investigations/agent_convention_survey.md
- .agents/investigations/effective_configuration_2026-09.md
- .agents/investigations/install_mechanisms_2026-09.md
- .agents/investigations/jetbrains_annexation_2026-09.md
- .agents/investigations/lua_multiversion_2026-09.md
- .agents/investigations/luarocks_annexation_2026-09.md
- .agents/investigations/node_multiversion_2026-09.md
- .agents/investigations/npm_annexation_2026-09.md
- .agents/investigations/package_environment_synthesis_2026-09.md
- .agents/investigations/pip_annexation_2026-09.md
- .agents/investigations/python_multiversion_2026-09.md
- .agents/investigations/runtime_synthesis_2026-09.md
- .agents/investigations/vscode_annexation_2026-09.md
- .agents/investigations/windows_config_candidates_2026-09.md
- .agents/investigations/windows_native_toolchain_annexation_2026-09.md
- .agents/platforms/linux_installation_scope.md
- .agents/platforms/symlink_runtime_notes.md
- .agents/platforms/windows_installation_scope.md
- .agents/platforms/windows_posix_shell_adapter.md
- .agents/scrcpy_virtual_screen_manager.md

## Human-facing governance surface

A-040/A-050 should cross-check current authority and navigation against AGENTS.md, the agent-lineage/CI and documentation-style docs, task/reminder/initiative lifecycle docs, and other architecture docs when repository-wide searches or links make them relevant.

## Known high-confidence cleanup already visible

- autonomic_affairs/reminders.md still says reminders become executable when specified for agent_tasks; current naming is tasks.
- The current task-storage contract retains two recent completed blocks; human direction supersedes this with archive-all-terminal-blocks.
- The seven terminal blocks listed above remain physically active and must be archived by A-020.
- The later .agents audit must err toward retention when relevance or historical value is uncertain.

## Boundary confirmation

- HOUSEKEEPING-A is the only authorized executable block.
- MSHP-WINGET-A remains frozen.
- Terminal states have not been rewritten.
- No block has yet been archived by HOUSEKEEPING-A.
- No reminder or initiative has been promoted.
- No memory/instruction cleanup has yet been performed.
