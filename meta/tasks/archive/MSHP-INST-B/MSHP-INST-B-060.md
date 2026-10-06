# MSHP-INST-B-060 — Integrate scoped installation lifecycle

## Description

Close the current installation-scope implementation phase after WinGet and Apt use the shared scoped ownership lifecycle.

Validate the architecture end to end, document current supported coverage, preserve future package-manager gaps in the initiative, and explicitly clear the Windows configuration-candidate investigation to resume.

## Requirements

- Add end-to-end integration tests spanning:
  - scoped strategy policy;
  - discovery candidates;
  - scoped provenance;
  - install post-verification;
  - check ownership;
  - exact uninstall;
  - user/machine coexistence;
  - legacy-state refusal/reconciliation.
- Ensure broad status/human/JSON output makes candidate scope and managed ownership understandable without introducing an overall health score.
- Ensure old scope-less provenance is surfaced honestly as legacy/unreconciled when not safely migrated.
- Update `INSTALLATION_ARCHITECTURE.md`, `INSTALLATION_SCOPE.md`, support/status docs, and durable agent notes to describe implemented scope behavior rather than future design.
- Update `MSHP-INST-SCOPE` current coverage:
  - core scope semantics implemented;
  - WinGet explicit USER/MACHINE behavior implemented;
  - Apt fixed MACHINE behavior implemented;
  - unsupported Flatpak/Homebrew/pipx/etc. remain structured OPEN gaps with no zombie tasks;
  - cross-account user mutation remains an intentional gap unless earlier implementation proves otherwise.
- Review the installation-takeover reminder for compatibility only; do not promote it.
- Explicitly record that `MSHP-APPS-A-010` may resume and that managed WinGet settings/preferences cannot change Machine-Soul-controlled install scope.
- Do not make `MSHP-APPS-A-010` structurally depend on this task; its scheduling relationship is policy/priority, not architecture.
- Run the full CI matrix on the final implementation head.

## Constraints / non-goals

- Do not implement deferred package managers.
- Do not close `MSHP-INST-SCOPE` merely because current WinGet/Apt support is complete.
- Do not implement installation takeover.
- Do not add application config integrations from `MSHP-APPS-A-010` in this task.

## Acceptance criteria

- Current managed WinGet and Apt installations have deterministic explicit scope semantics.
- Scoped provenance and exact candidate matching are validated across supported platforms.
- Ambient WinGet settings cannot silently change Machine-Soul install scope.
- Deferred future managers live only as initiative gaps until separately promoted.
- The Windows config-candidate investigation is explicitly safe to resume.
- Full CI is green.

## Validation

- Run all Python/unit integration suites plus Windows/Linux/fresh-clone CI.
- Exercise representative user-only, machine-only, dual-scope, legacy, wrong-scope, unmanaged, and exact-uninstall cases.
- Review initiative/task/reminder state for accidental execution authorization or zombie tasks.
