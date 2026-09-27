# Application operation contract

## 1. Paired application surfaces

Configuration content and operational machinery intentionally live in separate but parallel trees:

```text
assimilation_directives/<application>/
    # canonical tracked configuration files

annexation_procedures/<application>/
    # Apply / Unapply / Check / Install / Uninstall entry points
```

An application's operational surface may contain:

```text
annexation_procedures/<application>/
├── windows/
│   ├── apply_config.ps1
│   ├── unapply_config.ps1
│   ├── check_config.ps1
│   ├── install.ps1
│   └── uninstall.ps1
└── linux/
    ├── apply_config.sh
    ├── unapply_config.sh
    ├── check_config.sh
    ├── install.sh
    └── uninstall.sh
```

Not every application or platform needs every operation.

Shared configuration-deployment runtime code under `accumulated_instruments/configuration_deployment/` implements common semantics so these annexation adapters stay thin.

## 2. Required versus optional operations

For a configured application/platform pair:

- `apply_config` — required;
- `unapply_config` — required;
- `check_config` — required.

Install/Uninstall are optional until a safe strategy is implemented.

Every missing operation must be classified explicitly as:

- `SUPPORTED`;
- `UNSUPPORTED` — intentionally not applicable;
- `NOT_IMPLEMENTED` — desired but unfinished.

Absence of a file alone is not the capability contract.

## 3. Common inputs

Operations should support common operation-context inputs while defaulting safely:

- `MACHINE_SOUL` / repository root;
- discovered host identity;
- logical target account, defaulting to the current account;
- non-interactive mode;
- conflict policy;
- structured output mode when implemented.

Cross-account selection is one shared operation input, not a separate application-specific operation. The resolved target account is passed into shared engines and declarations; wrappers do not rediscover or reinterpret it.

Host/account auto-detection must be inspectable and overridable for testing. Legacy environment overrides may remain during migration, but the long-term user-facing account selection is an explicit operation option/context field.

## 4. Output contract

Human output should be concise and explain:

- operation;
- application;
- host/account target;
- source and destination when relevant;
- resulting state;
- action required when blocked.

Machine-readable output should be added when the shared runtime needs it, preferably without requiring external parser dependencies.

At minimum, Check emits one canonical state token:

```text
APPLIED
NOT_APPLIED
CONFLICT
WRONG_TARGET
BROKEN
UNSUPPORTED
ERROR
```

Additional installation-state tokens may include:

```text
INSTALLED_MANAGED
INSTALLED_UNMANAGED
NOT_INSTALLED
NOT_IMPLEMENTED
```

## 5. Exit semantics

Keep exit codes coarse; exact state belongs in the emitted status token.

Suggested shared contract:

- `0` — requested operation succeeded / Check is `APPLIED`;
- `1` — safe non-success state requiring no crash semantics (for example not applied/conflict/wrong target/broken);
- `2` — unsupported or not implemented;
- `3` — unexpected operational error.

Application-specific adapters must not invent incompatible meanings for these codes without documenting why.

## 6. Apply contract

Apply must:

- resolve one complete tracked source file per destination;
- classify destination before mutation;
- ask before replacing unmanaged state unless explicit non-interactive policy says otherwise;
- preserve displaced state;
- create a file-level symlink;
- verify it;
- record successful state only after verification;
- remain idempotent.

## 7. Unapply contract

Unapply must:

- establish current ownership before removing anything;
- remove only understood managed symlinks;
- restore displaced state when recorded and safe;
- refuse blind overwrite of unexpected current state;
- remain idempotent where practical.

## 8. Check contract

Check is read-only.

It must not repair or mutate state.

It reports the current relationship between:

- expected tracked source;
- native destination;
- deployment metadata;
- actual filesystem object.

## 9. Install contract

Install must:

- inspect current installation first;
- avoid claiming ownership of pre-existing unmanaged installs;
- use the declared strategy for the current platform;
- elevate only when needed;
- verify resulting application presence;
- record Hivemind installation provenance only after success.

## 10. Uninstall contract

Uninstall must:

- inspect current application and recorded install provenance;
- refuse casual automatic removal of an unmanaged/pre-existing install;
- invoke the declared uninstall strategy;
- verify the result;
- update installation state only after success.

## 11. Dry-run / planning

Shared operations should eventually support a non-mutating plan/dry-run mode where useful.

A dry run must not create backups, state records, directories, symlinks, packages, or other persistent side effects.

## 12. Application-specific exceptions

Some applications will have unusual config behavior.

Exceptions are allowed, but must be documented in the application module and should reuse the shared primitives wherever possible rather than bypassing safety rules.
