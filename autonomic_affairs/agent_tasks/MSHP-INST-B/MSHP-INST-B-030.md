# MSHP-INST-B-030 — Make installation ownership candidate-exact

## Description

Refactor install/check/uninstall safety to use typed installation discovery candidates plus scoped provenance rather than the old one-boolean `_is_installed` model.

This establishes the common ownership lifecycle both WinGet and Apt will use.

## Requirements

- Add shared selection/matching logic that relates a strategy's scope policy, scoped provenance, and one or more discovered `InstallationCandidate` objects.
- Preserve multiple candidates, including user and machine instances of the same package.
- Define exact managed-candidate matching using manager/package identity, actual scope, scope subject when applicable, and stronger native/uninstall identity when available.
- Treat scope-unknown legacy provenance as unreconciled unless a backend-specific later task proves it safe to upgrade.
- Refactor Install preflight:
  - if the intended scoped candidate is already exactly managed, report managed;
  - if a matching intended-scope candidate exists but is unmanaged, refuse to claim it;
  - candidates in other scopes do not automatically block installing the required scope when the backend permits coexistence;
  - ambiguity in the intended scope refuses mutation.
- Refactor post-install verification to rediscover and require one candidate compatible with the strategy scope contract before writing scoped provenance.
- Refactor Uninstall:
  - require exact scoped provenance;
  - rediscover and match exactly one owned candidate;
  - refuse ambiguity/mismatch rather than using package-manager defaults;
  - remove only the matching scoped provenance after successful backend removal.
- Apply the shared non-current user-scope guard before backend mutation.
- Keep `check_installed` broad/candidate-rich; add structured ownership/scope relation rather than collapsing dual-scope state into a boolean.
- Preserve Install/Uninstall dry-run safety and report intended target scope/candidate data.
- Introduce backend hooks/helpers only where generic matching cannot construct native mutation arguments; do not branch on application IDs.

## Constraints / non-goals

- Do not add WinGet `--scope` behavior yet.
- Do not change Apt's commands yet.
- Do not auto-adopt unmanaged installations.
- Do not implement installation takeover.
- Do not silently reconcile legacy WinGet scope.
- Do not require unsupported future package-manager identities.

## Acceptance criteria

- Generic installation ownership no longer depends on one unscoped installed boolean.
- Dual-scope candidates can coexist without being collapsed.
- Managed mutation requires exact scope-compatible provenance/candidate matching.
- Post-install scope mismatch fails without creating ownership.
- Uninstall cannot target a different scoped instance merely because it shares a package ID.
- Cross-account user mutation is refused before backend execution.

## Validation

- Unit-test managed/unmanaged intended scope, other-scope-only presence, dual-scope coexistence, intended-scope ambiguity, legacy unknown state, post-install scope mismatch, and exact uninstall selection.
- Ensure dry-run does not mutate state.
- Run installation/discovery/orchestration tests and full CI.
