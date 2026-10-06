# MSHP-INST-A-040 — Synthesize installation scope roadmap

## Description

Synthesize the installation-scope semantic, Windows, and Linux-extensibility investigations into an executable implementation roadmap.

The implementation roadmap should prioritize a correct core model and current Windows/Apt behavior without pretending every future package manager must be implemented before the architecture is useful.

## Requirements

- Consume the durable/workspace outputs of `MSHP-INST-A-010`, `MSHP-INST-A-020`, and `MSHP-INST-A-030`.
- Reconcile any contradictions between abstract scope semantics and actual WinGet/Apt/platform behavior.
- Update the `MSHP-INST-SCOPE` initiative with:
  - implemented/planned current coverage;
  - explicitly known deferred gaps;
  - deliberate boundaries;
  - related implementation tasks;
  - criteria for eventual initiative completion.
- Distill permanent architecture decisions into human docs and expensive-to-rediscover findings into `.agents/`.
- Create bounded executable implementation tasks justified by the investigation. Expected seams to evaluate include, but are not predetermined:
  - core requested/actual scope model;
  - InstallState scope/provenance migration;
  - machine-scoped versus account-scoped ownership storage;
  - explicit WinGet scope mutation/uninstall targeting;
  - Apt declared machine scope;
  - discovery reconciliation/validation of actual versus requested scope;
  - cross-account user-scope refusal or support mechanism.
- Permit a Windows/core implementation roadmap to become fully COMPLETE while the installation-scope initiative remains OPEN for future Flatpak/Homebrew/pipx/etc. integrations.
- Do not create speculative tasks for package managers that Machine-Soul has no current reason to implement.
- Identify whether `MSHP-APPS-A-010` can safely resume after this synthesis, especially for WinGet settings, and record any relevant architecture dependency in its workspace/docs rather than inventing a false task dependency.
- Keep installation takeover as a separate reminder/initiative candidate unless explicitly promoted by the human.

## Constraints / non-goals

- Do not implement the newly created scope tasks in this synthesis task.
- Do not create a single permanently incomplete "support every package manager" task.
- Do not require initiative completion as a prerequisite for completing current implementation blocks.
- Do not silently make WinGet settings/defaults authoritative over Machine-Soul install scope.
- Do not promote unrelated reminders.

## Acceptance criteria

- A concrete scope implementation roadmap exists and is traceable to investigation evidence.
- Current Windows/core and Apt behavior can be implemented without waiting for unsupported future managers.
- Deferred Linux/package-manager gaps live clearly in `MSHP-INST-SCOPE`.
- Every created implementation task has bounded scope, dependencies, acceptance criteria, and validation.
- The initiative/task/reminder distinction is exercised successfully on a real multi-phase architectural concern.
- The Windows config-candidate investigation has a clear safe scheduling relationship to the completed scope synthesis.

## Validation

- Trace every created implementation task to a specific scope finding.
- Verify no task remains intentionally incomplete merely to represent future package-manager support.
- Verify the installation-scope initiative retains known gaps that have no tasks.
- Verify Dispatch and dependencies remain consistent with task rules.
- Verify `MSHP-APPS-A-010` remains independently identifiable rather than being incorrectly made part of the installation-scope block.
