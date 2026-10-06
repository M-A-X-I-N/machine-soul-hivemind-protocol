# MSHP-INST-SCOPE — Installation scope

**Status:** OPEN

## Goal

Make installation scope a first-class, safe Machine-Soul concept without requiring every current or future package manager to be implemented before the core model becomes useful.

Machine-Soul must distinguish:

- logical target account;
- OS execution identity;
- requested/actual installation scope;
- Machine-Soul ownership/provenance.

Package-manager defaults or user configuration must not silently redefine semantically important Machine-Soul scope intent.

## Current state / coverage

Current core and supported-backend scope semantics are implemented:

- mutation-side scope policy is first-class and separate from observed discovery scope;
- `AptPackage` is fixed MACHINE scope;
- `WingetPackage` carries an explicit required scope; current Oh My Posh management requires USER;
- WinGet managed mutation uses explicit `--scope`, and discovery checks user/machine scopes independently;
- scoped provenance supports simultaneous host/machine and host/user ownership records;
- install/uninstall ownership matching is candidate-exact and refuses intended-scope ambiguity;
- post-install verification must prove a compatible actual scope before ownership is recorded;
- scope-less legacy records are unreconciled by default; Apt can reconcile one exact compatible fixed-machine record;
- non-current target user mutation remains unsupported without a proven backend target-user execution mechanism;
- broad status preserves exact JSON candidate data and summarizes candidate scopes in human output.

The current INST-B implementation block covers the scope behavior of the package managers Machine-Soul actually mutates today. This initiative remains OPEN for deliberately deferred mechanisms and account/inventory capabilities.

## Known gaps

Known gaps are intentionally allowed to remain without executable tasks until Machine-Soul actually supports or needs the relevant mechanism.

Current known future areas include:

- Flatpak `--user` versus system installations;
- Homebrew/Linuxbrew prefix and ownership semantics;
- pipx or similar user-local application package managers;
- other package managers with scope concepts that differ materially from current Apt/WinGet models;
- cross-account user-scoped installation remains unsupported until a safe target-user execution/impersonation mechanism exists;
- complete other-user MSI/AppX inventory beyond current-user/machine needs;
- package-manager-specific discovery needed to prove actual scope for future backends.

## Deliberate boundaries / deferred work

- Windows/core scope correctness takes precedence over exhaustive future package-manager support.
- Apt is the concrete Linux mutation baseline; other Linux managers are used only to stress-test extensibility until separately promoted.
- Installation takeover/adoption/migration remains a separate reminder/concern. Scope work should make takeover possible to reason about, but does not authorize it.
- Windhawk is unrelated and remains a separate reminder.
- This initiative may remain OPEN after all current scope implementation tasks complete if future package-manager gaps remain intentional.

## Related executable tasks

Completed investigation work:

- `MSHP-INST-A-010` — core installation-scope semantics;
- `MSHP-INST-A-020` — Windows scope behavior;
- `MSHP-INST-A-030` — Linux extensibility stress-test;
- `MSHP-INST-A-040` — implementation-roadmap synthesis.

Current implementation block:

- `MSHP-INST-B-010` — scope policy model;
- `MSHP-INST-B-020` — scoped installation provenance;
- `MSHP-INST-B-030` — candidate-exact installation ownership;
- `MSHP-INST-B-040` — scoped WinGet mutation/discovery;
- `MSHP-INST-B-050` — Apt fixed machine scope;
- `MSHP-INST-B-060` — integrated validation/current-coverage closure.

The first five are implemented; B-060 records integration closure and the handoff back to application-config research.

Task state, dependencies, and Dispatch remain authoritative in [`../tasks.md`](../tasks.md); this list is contextual only.

## Promotion / closure criteria

Promote a known gap into executable work only when:

- Machine-Soul is adding/supporting the relevant package mechanism or application and scope behavior matters now;
- the behavior is sufficiently understood to write a bounded task;
- implementation will not require a permanently incomplete "support everything" task.

This initiative may become COMPLETE when all installation mechanisms Machine-Soul intentionally supports have explicit, safe scope semantics and the remaining known gaps are no longer part of the desired supported surface.

It may remain OPEN indefinitely without blocking completion of current Windows/core/Apt work.
