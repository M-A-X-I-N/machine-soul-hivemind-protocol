# MSHP-INST-B-010 — Implement scope policy model

## Description

Implement the mutation-side installation-scope policy model established by the INST-A investigations.

Observed installation scope remains discovery state. This task adds the separate declarative contract that tells a mutating installation strategy whether its scope is fixed, explicitly required, or intentionally delegated.

Do not change WinGet/Apt command construction yet.

## Requirements

- Add typed mutation-side scope policy/value types under the shared Python model.
- Preserve the existing discovery-side `InstallationScope` as observed actual state; do not overload it with request-policy semantics.
- Support the semantic modes justified by current research:
  - fixed scope;
  - required explicit scope;
  - intentionally delegated scope.
- Do not implement preferred-with-fallback until a supported backend actually needs it.
- Provide a shared compatibility function between requested/fixed policy and observed `InstallationScope`.
- Required/fixed `USER` must accept observed `USER` and may accept `PACKAGE_USER` only when the package-user subject is the intended current target account.
- Required/fixed `MACHINE` must accept only observed `MACHINE`.
- Add scope policy to installation strategies in a way that makes backend intent explicit.
- Declare `AptPackage` as fixed machine scope at the model level.
- Extend `WingetPackage` so each managed package must eventually declare an explicit required user or machine scope; update current declarations/tests to compile with the chosen policy but do not add CLI `--scope` behavior yet.
- Add a shared pre-mutation guard for user-scoped requests: reject a non-current target account unless a backend explicitly supplies a proven target-user mechanism.
- Keep execution identity conceptually distinct; the immediate guard may use `TargetAccount.is_current` but document that as the current evidence available, not the permanent identity model.
- Ensure dry-run can report the requested/fixed scope policy in structured result data once mutation tasks consume it.
- Update the durable installation-scope docs if concrete type names refine the earlier conceptual language.

## Constraints / non-goals

- Do not change install-state storage/schema in this task.
- Do not pass WinGet `--scope` yet.
- Do not refactor install/uninstall ownership around discovery candidates yet.
- Do not add Flatpak, Homebrew, pipx, or other package-manager strategies.
- Do not implement cross-account impersonation.
- Do not implement installation takeover.

## Acceptance criteria

- Mutation scope policy is a typed first-class model independent from observed discovery scope.
- Apt declares fixed machine scope.
- WinGet-managed declarations cannot accidentally rely on ambient scope without an explicit policy choice.
- Scope compatibility semantics are unit-tested, including `PACKAGE_USER` compatibility rules.
- Non-current user-scoped mutation can be refused through a shared guard before any backend command runs.
- Existing non-scope application/config behavior remains green.

## Validation

- Unit-test fixed/required/delegated policy construction and invalid combinations.
- Unit-test USER/MACHINE/PACKAGE_USER/UNKNOWN compatibility.
- Unit-test current versus non-current target-account user-scope guards.
- Run the Python declaration/model tests and full CI.
