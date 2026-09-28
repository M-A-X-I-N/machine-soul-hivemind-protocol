# Installation scope semantics

Machine-Soul treats installation scope as a first-class concept distinct from logical target account, execution identity, and installation ownership.

## Four independent identities

### Target account

The **target account** is the logical account Machine-Soul is acting for. It selects account-specific desired state and configuration destinations.

Target account does not imply that a package is installed only for that user, and it does not prove which OS identity executes a package-manager process.

### Execution identity

The **execution identity** is the OS account/security context that actually runs a command.

Elevation, sudo, and future impersonation mechanisms affect execution identity/permissions. They do not by themselves define installation scope.

### Installation scope

The **installation scope** describes the population/registration domain to which the installed application belongs.

The existing discovery-side `InstallationScope` remains an observed-state classification:

- `USER` — user-scoped installation;
- `MACHINE` — machine/system-scoped installation;
- `PACKAGE_USER` — package-registration semantics tied to one package user, such as current-user AppX/MSIX evidence;
- `UNKNOWN` — scope could not be established safely.

Backend-specific details such as package family, prefix, installation root, Flatpak installation name, or registry view remain structured evidence/metadata rather than exploding the core enum.

### Machine-Soul ownership / provenance

Ownership answers whether Machine-Soul has sufficient matching provenance to mutate/remove a specific installation candidate.

Ownership never follows merely from preferred mechanism, target account, scope, or package-manager correlation.

## Mutation scope contract

Observed scope and requested scope are different types of fact.

A mutating installation strategy must declare how its scope is determined. The core architecture should support these semantic modes:

1. **Fixed scope** — the backend/strategy inherently installs into one known scope. Apt is the current example: an `AptPackage` mutation is machine/system scoped.
2. **Required explicit scope** — Machine-Soul chooses one required scope and instructs the backend to target it. WinGet user/machine installation is the expected current example.
3. **Delegated scope** — the backend/package-manager is explicitly allowed to choose. This must be an intentional strategy decision, not the accidental result of omitting a scope flag.

A future backend may justify a **preferred scope with explicitly allowed fallback**, but that should be added only when a real supported manager needs it. It must never mean unconstrained package-manager fallback.

### Determinism invariant

> Machine-Soul-managed package mutation must not allow package-manager configuration, user preferences, ambient defaults, or installer ordering to silently change a semantically important scope.

For fixed or required scope, mutation must either produce/verify the requested scope or fail without recording ownership.

## Cross-account user scope

User-scoped mutation is safe only when the package manager operates in the same user/security context whose installation is being targeted, unless a backend provides a separately proven impersonation/target-user mechanism.

Initial core rule:

> If a user-scoped installation targets a non-current logical account and no backend-specific proven target-user mechanism exists, refuse the mutation as unsupported before running the package manager.

`TargetAccount.is_current` can participate in the immediate implementation, but the durable model should treat execution identity explicitly rather than assuming target account and process identity are synonymous.

Machine-scoped mutation may legitimately use an elevated execution identity different from the target account because the installation itself is host-scoped.

## Provenance scope and storage

Installation provenance should identify both requested and actual scope.

A future scoped `InstallState` should carry at least:

- application identity;
- host identity;
- package manager/backend identity;
- package/product identity;
- requested scope policy/result;
- actual verified scope;
- user/account subject when the actual scope is user/package-user;
- backend-specific identity needed for exact uninstall targeting;
- optional audit metadata about the execution identity that performed the mutation.

### Ownership namespace

Provenance ownership follows actual installation scope:

- user/package-user scoped state belongs under the host + target/subject account namespace;
- machine-scoped state belongs under a host-level machine namespace, not under whichever user happened to request installation;
- unknown-scope state is legacy/unreconciled evidence and must not become authoritative ownership merely by existing.

The precise on-disk state path is an implementation decision for the synthesis task, but the semantic ownership boundary is fixed here.

## Legacy state

Existing `InstallState` records have no scope field.

On read/migration they must be treated as scope-unknown until reconciled safely. A backend with an inherently fixed scope may be able to upgrade the record when current discovery proves the same installation candidate. A historical WinGet record must not be guessed to user or machine scope merely from `manager=winget`.

Legacy scope-unknown provenance must not authorize uninstall of a potentially different scoped instance.

## Coexisting scopes

The same logical package may exist simultaneously at user and machine scope.

Discovery must retain those candidates separately. Install/check/uninstall must match the intended candidate using at least package identity + actual scope + scope subject when applicable, plus stronger native identity where available.

If Machine-Soul provenance cannot uniquely match one discovered candidate, mutation must refuse rather than choose one based on PATH or package-manager defaults.

## Relationship to discovery

Discovery owns facts about actual candidates and actual scope. Mutation policy owns what scope Machine-Soul intended/required.

A successful install is not complete for ownership purposes until post-mutation discovery/verification establishes a candidate compatible with the strategy's scope contract.

Scope mismatch should be represented explicitly rather than hidden inside generic installed/unmanaged status.

## Current manager expectations

### Apt

- scope contract: fixed `MACHINE`;
- sudo/root: execution mechanism only;
- target account: does not own the system package;
- provenance should ultimately be host/machine scoped.

### WinGet

- current implementation is unsafe-by-omission with respect to scope because it passes no explicit scope;
- expected contract is required explicit `USER` or `MACHINE` for Machine-Soul-managed mutations unless Windows investigation proves a narrower safe rule;
- WinGet settings/preferences must not override Machine-Soul's chosen scope.

## Implementation boundary

This document defines semantics, not code. `MSHP-INST-A-020` and `MSHP-INST-A-030` test the model against real Windows/Linux mechanisms. `MSHP-INST-A-040` creates the evidence-based implementation tasks.

## Windows platform findings

WinGet is the primary current selectable-scope mutation backend.

- Machine-Soul-managed WinGet mutation should use an explicit required `user` or `machine` scope rather than WinGet's ambient preference/fallback behavior.
- Scoped WinGet discovery should query user and machine installed scopes separately and preserve coexisting candidates.
- WinGet uninstall should scope-filter the exact managed installation and refuse ambiguity.
- Requested core `USER` may map to observed native `USER` or current-target `PACKAGE_USER`; requested `MACHINE` requires observed machine scope.
- User-scoped WinGet/AppX mutation for a non-current target account is initially unsupported.
- MSI/ARP current-user versus machine scope is directly observable from registration context; complete other-user inventory is deferred.
- AppX provisioning for future users is not treated as the same concept as a machine-scoped installed application.

The current Oh My Posh WinGet manifest is an explicit regression edge because it is AppX/MSIX without a manifest `Scope:` field. Scoped implementation must test WinGet's behavior and verify native package-user registration rather than relying solely on manifest scope metadata.

Detailed Windows research is preserved in the active `MSHP-INST-A` workspace until synthesis.
## Linux extensibility findings

The core scope model also survives representative Linux package-manager patterns without becoming manager-specific.

- Apt/dpkg is a fixed `MACHINE` backend; sudo/root affects execution identity only.
- Flatpak uses explicit per-user and system installations and may have multiple **named system installations**. A Flatpak backend would therefore use core USER/MACHINE scope plus a backend installation-name identity.
- pipx defaults to user-local roots and supports `--global` all-users installation with independently configurable roots. A pipx backend would use core USER/MACHINE plus its resolved path metadata.
- Homebrew/Linuxbrew is organized around one owning account and a prefix rather than a package-level `--user`/`--system` switch. A future backend must preserve prefix + owner identity and should decide the appropriate coarse scope only when actual Homebrew support is designed.

These examples reinforce the boundary: the core owns coarse scope policy/compatibility/provenance semantics; each backend owns native selectors, exact installation identity, roots/prefixes, and scope verification.

Unsupported managers remain gaps in `MSHP-INST-SCOPE`, not permanently incomplete tasks.