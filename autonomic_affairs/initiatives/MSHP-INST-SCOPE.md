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

- Installation discovery already records observed candidate scope as user, machine, package-user, or unknown.
- Mutating `AptPackage` and `WingetPackage` strategies do not yet carry explicit scope policy.
- `InstallState` provenance does not yet record installation scope.
- Apt mutation is effectively machine/system scoped but provenance is currently stored beneath a target-account namespace.
- WinGet mutation currently omits `--scope`, so WinGet/package defaults can influence actual scope.
- `MSHP-INST-A-010` has now defined the core semantic contract: observed scope is separate from mutation scope policy; managed mutation must be fixed-scope, explicitly required-scope, or intentionally delegated; unknown legacy scope cannot authorize ambiguous uninstall.
- `MSHP-INST-A-020` confirms the Windows-first shape: WinGet must use explicit required scope; discovery/list and uninstall must be scope-filtered; current-user/package-user and machine candidates stay distinct; cross-account user mutation is initially unsupported.
- `MSHP-INST-A-030` confirms the core model remains extensible: Apt is fixed machine scope; Flatpak/pipx fit user-versus-machine with backend-specific installation/root identity; Homebrew demonstrates that prefix + owning account can matter more than a simple package scope flag.
- The synthesis task now turns the current Windows/core/Apt findings into bounded implementation work while leaving unsupported managers here as intentional gaps.

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

Current investigation work:

- `MSHP-INST-A-010` — define core installation-scope semantics;
- `MSHP-INST-A-020` — investigate Windows scope behavior;
- `MSHP-INST-A-030` — investigate Linux extensibility;
- `MSHP-INST-A-040` — synthesize the implementation roadmap.

Task state, dependencies, and Dispatch remain authoritative in [`../agent_tasks.md`](../agent_tasks.md); this list is contextual only.

## Promotion / closure criteria

Promote a known gap into executable work only when:

- Machine-Soul is adding/supporting the relevant package mechanism or application and scope behavior matters now;
- the behavior is sufficiently understood to write a bounded task;
- implementation will not require a permanently incomplete "support everything" task.

This initiative may become COMPLETE when all installation mechanisms Machine-Soul intentionally supports have explicit, safe scope semantics and the remaining known gaps are no longer part of the desired supported surface.

It may remain OPEN indefinitely without blocking completion of current Windows/core/Apt work.
