# MSHP-INST-A-010 — Define installation scope semantics

## Description

Investigate and define installation scope as a first-class Machine-Soul concept.

The current architecture has a first-class logical target account and rich discovery-side installation scope, but mutating install strategies and persisted installation provenance do not yet explicitly model whether an installation is user-scoped, machine-scoped, or otherwise scoped.

This task establishes the semantic model before platform-specific implementation is designed.

## Requirements

- Inspect the current operation context, installation strategies, installation discovery assessments, InstallState persistence, install/uninstall safety rules, and target-account/session model.
- Define and clearly separate at least:
  - **target account** — the logical account Machine-Soul is configuring/acting for;
  - **execution identity** — the OS identity actually running the package-manager command;
  - **installation scope** — who/what the installed software is made available to;
  - **Machine-Soul ownership/provenance** — whether Machine-Soul is authorized to manage/remove the discovered installation.
- Decide the minimal first-class scope vocabulary needed by the core model. Evaluate at least:
  - user;
  - machine/system;
  - package-manager/application-specific scope where user/machine is insufficient;
  - unknown;
  - automatic/default/preferred scope as a *request/policy* concept rather than an observed scope, if useful.
- Distinguish requested/preferred/required installation scope from discovered actual scope.
- Define whether installation strategies should declare:
  - fixed inherent scope;
  - required scope;
  - preferred scope with controlled fallback;
  - explicitly delegated/default scope;
  - or a small combination of these.
- Define the invariant for Machine-Soul-controlled mutation: package-manager/user configuration must not silently change a semantically important requested scope unless the strategy explicitly allows delegation/fallback.
- Define how scope belongs in persisted installation provenance and how old state lacking scope should be interpreted/migrated.
- Examine whether machine-scoped install state should remain stored beneath a target-account namespace or move/be indexed by a host/machine ownership location.
- Define uninstall matching requirements when user- and machine-scoped instances of the same package may coexist.
- Define behavior for user-scoped installation when `target_account` is not the current execution account:
  - supported through a proven impersonation/native mechanism;
  - explicitly unsupported;
  - or another safely justified model.
- Reconcile the mutation-side model with the existing discovery-side `InstallationScope` semantics without forcing them to be identical if request-policy and observed state need different types.
- Record conclusions in the `MSHP-INST-SCOPE` initiative and promote durable architecture decisions to normal docs/`.agents/`.

## Constraints / non-goals

- Do not implement WinGet/Apt scope flags in this task.
- Do not redesign target-account semantics unrelated to installation.
- Do not assume target account equals execution identity.
- Do not treat package-manager defaults as an acceptable implicit core policy without documenting that choice explicitly.
- Do not attempt to support every Linux/package-manager scope variant.
- Do not implement installation takeover.
- Do not block the eventual Windows implementation merely because future managers have additional scope shapes.

## Acceptance criteria

- Target account, execution identity, installation scope, and Machine-Soul ownership have explicit non-overlapping definitions.
- The core architecture has a proposed scope request/policy model and observed/provenance model capable of representing current Windows and Apt behavior without lying.
- Cross-account user installation has an explicit safety/support rule.
- Machine-scoped provenance ownership/storage has an explicit proposed treatment.
- Coexisting user/machine installations can be represented and safely targeted for uninstall.
- The result provides concrete questions/interfaces for the Windows and Linux investigation tasks rather than hand-waving scope to package-manager defaults.

## Validation

- Walk scenarios including:
  - current user + user-scoped install;
  - current user + machine-scoped install;
  - non-current target account + user-scoped request;
  - package present at both user and machine scope;
  - package manager default changes independently of Machine-Soul;
  - old provenance lacking scope;
  - discovery reports a scope different from requested/provenance scope.
- Verify the proposed semantics align with existing installation-discovery candidate data.
- Review the installation takeover reminder only for compatibility; do not promote or implement it.
