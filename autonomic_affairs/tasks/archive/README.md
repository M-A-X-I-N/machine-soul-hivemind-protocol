# Agent task archive

This directory preserves terminal task blocks that have left the active scheduling view. A block belongs here once every task in it is terminal (`COMPLETE`, `CANCELLED`, or `SUPERSEDED`).

Archived new-style blocks retain their directory structure, including any block/task-scoped `workspace/`. Task IDs remain permanent identities even though their paths move.

Before archival, durable conclusions should be promoted to source/tests, human-facing documentation, or `.agents/` as appropriate. Remaining workspace material is historical context and need not be read during normal startup.

## Legacy V2

Legacy tasks `V2-01` through `V2-63` were maintained before per-task specification files existed. Their original definitions are preserved together under `V2/` rather than manufacturing a new file structure after the fact.

The legacy V2 series completed on 2026-09-27 after the Python/declarative runtime, platform-neutral atomic wrappers, legacy-runtime retirement, wrapper-driven orchestrator, and end-to-end Windows/Linux/fresh-clone validation passed.


## MSHP-META-A

The completed `MSHP-META-A` block is preserved under `MSHP-META-A/`.

This block established the modern repository self-management substrate: thematic meta naming, structured task lifecycle/workspaces/archive, generic machine identities, agent provenance, reminders, maintainer-language policy, runtime relocation into `annexation_procedures/`, and promotion of the active iteration to `main`.

It cycled out of the active scheduling index on 2026-09-28 after the newer completed `MSHP-DISC-A` and `MSHP-DISC-B` blocks became the two retained context blocks.


## MSHP-META-B

The completed `MSHP-META-B` block established the lightweight initiative layer between reminders and executable tasks, and created `MSHP-INST-SCOPE` as the first structured non-executable initiative.

It cycled out after the newer completed `MSHP-INST-B` and `MSHP-APPS-A` blocks became the two retained active-context blocks.


## MSHP-INST-A

The completed `MSHP-INST-A` block defined installation-scope semantics, researched Windows and representative Linux package-manager scope behavior, and synthesized the scoped-installation implementation roadmap.

Its workspace is preserved intact with the archived block; durable conclusions were promoted into installation docs, `.agents/`, and `MSHP-INST-SCOPE`.


## MSHP-DISC-A

The completed `MSHP-DISC-A` block defined discovery semantics, investigated installation and effective-configuration discovery, normalized structural configuration checks, and synthesized the discovery implementation roadmap.

Its research workspace remains preserved with the archived block.


## MSHP-DISC-B

The completed `MSHP-DISC-B` block implemented typed discovery assessments, Linux/native-Windows/Windows-POSIX installation discovery, `verify_config`, shell/native/Oh My Posh verification, and integrated three-dimensional status reporting.


## MSHP-DEV-A

The terminal `MSHP-DEV-A` block preserves the completed developer-environment investigation and synthesis work covering editors, runtimes, multiversion behavior, and runtime package ecosystems.

## MSHP-DEV-B

The terminal `MSHP-DEV-B` block preserves the completed first implementation/research phase for developer annexation, including editor installation, native toolchain discovery, multiversion runtimes, package environments, and integrated lifecycle validation.

## MSHP-OPS-A

The terminal `MSHP-OPS-A` block preserves the original agent-lineage/selective-CI control-plane design, reusable validation extraction, dispatcher implementation, and validation experiments. Later OPS-D policy supersedes portions of its live routing design; this block remains historical evidence.

## MSHP-OPS-B

The terminal `MSHP-OPS-B` block preserves the CodeQL advanced-analysis investigation and the earlier separate deferred-analysis integration. Later OPS-D policy supersedes the separate-routing design while retaining relevant evidence.

## MSHP-APPS-A

The terminal `MSHP-APPS-A` block preserves the Windows configuration-candidate investigation that feeds the still-open `MSHP-WIN-CONFIG` initiative.

## MSHP-OPS-C

The terminal `MSHP-OPS-C` block preserves lineage-authority hardening, active claims, task-ledger readability, top-level directory contracts, and the `agent_tasks` to `tasks` migration.

## MSHP-OPS-D

The terminal `MSHP-OPS-D` block preserves the centralized CI-policy investigation, implementation plan/execution evidence, and final selector/shared-runner/CodeQL cutover validation.
