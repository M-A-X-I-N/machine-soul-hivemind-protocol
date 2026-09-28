# Configuration deployment contract

## 1. Scope

This contract governs Apply, Unapply, and Check for tracked configuration files.

Application installation/removal is separate and must not be conflated with configuration deployment.

## 2. Apply

For one managed file, Apply follows:

```text
resolve source
  ↓
validate source + destination parent + permissions
  ↓
classify current destination
  ↓
if unmanaged state exists:
    ask/obey explicit conflict policy
  ↓
preserve displaced state
  ↓
create expected file symlink
  ↓
verify resulting symlink and target
  ↓
record deployment state
```

If a failure occurs after displacement but before successful verified completion, Apply should restore the prior state immediately where practical.

A failed Apply must not intentionally leave the user worse off than before invocation.

## 3. Existing destination policy

Interactive default:

```text
Existing unmanaged configuration detected:
<path>

Preserve it and replace it with the Machine-Soul managed link? [y/N]
```

Default answer is No.

Non-interactive callers must provide an explicit conflict policy.

Initial policies:

- `abort` — make no change when replacement is required;
- `backup-and-replace` — preserve existing state then deploy.

There is deliberately no policy whose meaning is “delete whatever exists without preserving it.”

## 4. Backup storage

Displaced state lives under:

```text
$MACHINE_SOUL/scratch/backups/
```

Backup paths must avoid collisions across host, account, application, destination, and repeated deployments.

The exact encoding may evolve, but a backup must remain traceable from deployment metadata.

Backup storage is not Git history and is not a substitute for tracking canonical configuration.

## 5. Deployment metadata

Machine-local deployment records live under:

```text
$MACHINE_SOUL/scratch/state/
```

A record should contain enough information to reason safely about ownership and restoration, including as applicable:

- schema/version;
- application;
- host;
- account;
- platform;
- canonical source path relative to `$MACHINE_SOUL`;
- absolute destination path;
- observed prior destination type;
- backup path when one exists;
- successfully applied target;
- timestamps useful for diagnostics;
- operation/tool version when useful.

State records must not contain secrets.

## 6. Ownership

The configuration-deployment runtime may mutate/remove a destination without prompting only when it can prove the current object is the expected managed state for the operation.

A remembered state record alone does not authorize overwriting current filesystem reality.

Example:

1. Apply creates the expected link.
2. A human later replaces that link with a regular file.
3. Unapply runs.

Unapply must report a conflict. It must not delete the human's new file merely because an old backup exists.

Core rule:

> Only mutate objects whose current state is understood.

## 7. Unapply

For a managed file:

```text
load/resolve expected ownership
  ↓
classify current destination
  ↓
verify it is the managed object expected
  ↓
remove managed symlink
  ↓
restore displaced prior state if recorded and safe
  ↓
verify restoration/removal
  ↓
update/remove deployment state
```

Unapply is idempotent where possible.

If nothing is applied and there is no safe restoration pending, it should report that fact rather than fail destructively.

## 8. Restore semantics

The desired lifecycle is:

```text
original destination
      ↓ Apply
backup original + create managed symlink
      ↓ Unapply
remove managed symlink + restore original
```

Restoration should preserve the prior object as faithfully as practical, including whether it was a regular file or a symlink.

Unexpected destination changes block automatic restore until explicitly resolved.

## 9. Transactionality

Filesystem operations are not universally transactional, so the configuration-deployment runtime uses transactional intent:

1. preflight validation before destructive mutation;
2. preserve recoverable prior state first;
3. perform the smallest mutation necessary;
4. verify after each critical step;
5. record success only after verification;
6. roll back immediately when a later step fails and safe rollback is possible.

State metadata must not claim successful deployment before the filesystem actually reflects it.

## 10. Idempotency expectations

Supported operations should behave predictably when repeated.

Expected lifecycle test:

```text
Check
Apply
Check
Apply again
Unapply
Check
Unapply again
```

Repeated Apply against the already-correct managed link should not create a new backup or unnecessarily mutate the filesystem.

Repeated Unapply after a completed unapply should not destroy restored unmanaged state.

## 11. Check is structural and read-only

Check inspects both current destination structure and the relationship to Machine-Soul deployment metadata without mutating either.

The primary result code describes the native destination: `applied`, `not_applied`, `conflict`, `wrong_target`, or `broken`. Structured result data separately reports Machine-Soul ownership/state relationship.

An exact expected symlink with no recorded state is still structurally applied, but Machine-Soul ownership is unproven. Conversely, stale recorded state must be surfaced rather than silently treated as proof of current ownership.

Check does not prove application installation or runtime/effective configuration use. Effective verification is the separate `verify_config` concept defined in `DISCOVERY_SEMANTICS.md`.

## 12. Checkout relocation

Because native symlinks contain concrete targets, moving `$MACHINE_SOUL` may make existing links stale.

Check must surface this as `WRONG_TARGET` or `BROKEN` as appropriate and may additionally identify the link as `managed_stale_link` when deployment state proves the relationship to the previous checkout target. Check must not repair it.

Apply may repair a stale previously-managed link only after safely establishing its relationship to the repository/state; it must not blindly classify every arbitrary wrong symlink as owned.

## 12. Cross-platform contract

Windows and Linux implementations may use different native APIs/tools, but must expose the same semantic behavior:

- same state vocabulary;
- same conflict policy;
- same preservation guarantees;
- same ownership rule;
- same Apply/Unapply/Check meaning.

Platform differences belong beneath the shared contract.
