# Account targeting contract

## Core rule

Every operation has one logical target account.

If the caller does not specify one, the target is the current account. Selecting another account is explicit and uses one common operation parameter rather than alternate per-account scripts.

Logical target identity is separate from process execution identity.

## Operation model

The future Python runtime should resolve account targeting before application-specific operation logic begins.

Conceptually:

```text
raw operation request
    + optional target account name
        ↓
shared account resolver
        ↓
resolved target account
        ↓
operation context
        ↓
application wrapper / shared operation engine
```

A resolved target should contain the information shared engines need, including at minimum the canonical account name, whether it is the current account, and its home/config root information.

The exact Python class/API names are intentionally left to V2-50+ implementation work.

## Defaults and explicit targeting

No explicit target means the current runtime account.

An explicit target, conceptually `--account root`, means all account-sensitive semantics belong to that target:

- account-specific assimilation-directive selection;
- native config destination;
- deployment state/provenance keys;
- install provenance when installation ownership is account-scoped;
- reporting/presentation.

Machine-Soul never silently falls back to the current account when an explicit target cannot be resolved.

## Elevation

Elevation is a permission mechanism, not account selection.

If the logical target is `root`, that target remains root before, during, and after any `sudo` primitive.

If the logical target is a normal account but a narrow operation requires elevation, running that primitive as root must not make root the logical target.

Do not run an entire workflow elevated merely to simplify one privileged step.

## Platform expectations

### Linux/POSIX

Use the local account database for explicit-account metadata rather than assuming `/home/<name>`. Python standard-library facilities such as `pwd` are suitable for local account lookup.

### Windows

Current-account discovery is supported by ordinary runtime/environment APIs.

Arbitrary other-account profile/home discovery and safe mutation is a separate capability. Until a reliable implementation exists, explicit non-current Windows targets must return an unsupported/unresolvable result rather than guessing a profile path.

## Management ownership

Account existence is not management intent.

A tracked account-specific config file is not management intent.

Only an explicit operation targeting an account (or an operation defaulting to the current account) creates/changes Machine-Soul state for that target.

## Legacy migration

The current shell/PowerShell implementation uses `MACHINE_SOUL_ACCOUNT` overrides in tests and some adapters. These may remain while migrating behavior, but they are transitional testing/plumbing inputs, not the final public account-selection interface.
