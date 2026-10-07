# Configuration model

## 1. Canonical root

`$MACHINE_SOUL` is the canonical absolute path of the active repository checkout.

Every repository-internal path used by configuration, deployment state, and application operations must be derived from it. Host-specific absolute checkout paths must not be committed.

Examples:

```text
Windows: C:\Users\...\machine-soul-hivemind-protocol
Linux:   /home/.../machine-soul-hivemind-protocol
```

The variable value differs by host; the meaning does not.

Moving the checkout therefore changes only the host's `$MACHINE_SOUL` binding. Existing symlinks may then become stale and must be detectable/repairable by Check/Apply.

A tracked root marker, `.machine_soul_root`, provides a stable repository-identity sentinel for runtime root discovery. Operational root detection must not depend on repository-administration artifacts such as the agent task ledger; those may move or evolve independently.

## 2. Paired taxonomy

Canonical configuration and the machinery that applies it are deliberately separated:

```text
assimilation/
└── <application>/
    ├── shared/
    ├── default/
    │   ├── common/
    │   └── users/
    │       └── <account>/
    └── hosts/
        └── <hostname>/
            ├── common/
            └── users/
                └── <account>/

annexation/
└── <application>/
    ├── _application.py
    ├── apply_config.py
    ├── unapply_config.py
    ├── check_config.py
    └── ...
```

`assimilation/` is the repository's configuration-content tree: the equivalent of a conventional top-level `config/` tree.

`annexation/` is the operational tree: the equivalent of a conventional top-level `operations/` tree.

The two are intrinsically paired by application name, but neither is nested inside the other.

Shared symlink/backup/state/dispatch implementation belongs under `annexation/` rather than being duplicated in each annexation procedure.

## 3. Configuration identity dimensions

A configuration may vary by:

1. application;
2. host;
3. operating platform/environment;
4. account/user;
5. optional application-specific variant where a real need appears.

Host and account remain useful configuration-selection dimensions, but Machine-Soul does not require a tracked registry of machines or accounts.

Runtime facts are discovered when practical:

- hostname from the operating environment;
- current account from the operating environment;
- platform/OS from the running platform or the platform-specific entry point;
- home/config roots from the target/current account environment;
- privilege state when an operation needs to know it.

Explicit environment overrides such as `MACHINE_SOUL_HOST` and `MACHINE_SOUL_ACCOUNT` remain useful for tests and unusual environments, but ordinary operation must not depend on a tracked host-inventory record.

The configuration tree currently contains multiple concrete host-specific variants. Their identities belong in `assimilation/<application>/hosts/<hostname>/` where they select genuinely different configuration; durable architecture documentation does not need to enumerate those machine names.

## 4. Resolution precedence

For a requested application file, resolution uses the most specific complete tracked file available:

```text
1. hosts/<host>/users/<account>/<file>
2. hosts/<host>/common/<file>
3. default/users/<account>/<file>
4. default/common/<file>
```

If no complete tracked file resolves, the configuration is unsupported/not configured for that target.

`shared/` is reusable source material, not a deployment fallback. A file under `shared/` is linked directly only when the application module explicitly declares it as the complete desired file. Otherwise applications may include/source shared fragments using their native mechanisms.

This avoids deployment-time content merging and preserves the invariant that the native config path points at one concrete tracked file.

## 5. File-level symlink invariant

Applying configuration means:

```text
native application config file
          │
          └── symbolic link ──> $MACHINE_SOUL/.../tracked-file
```

Rules:

- managed configuration is linked at the **file** level;
- normal Apply does not copy canonical config out of the repository;
- whole-directory links are not the default deployment mechanism;
- generated duplicate config files are not the canonical path;
- directories required to contain the destination may be created, but managed configuration ownership is tracked per file.

This makes edits through the application's normal config path edits to the Git working tree itself.

## 6. scratch/

`$MACHINE_SOUL/scratch/` is machine-local mutable state and must remain Git-ignored.

Expected uses include:

```text
scratch/
├── backups/
├── state/
├── env/
├── temp/
├── logs/
└── cache/
```

Only create subdivisions that are actually needed.

No tracked configuration may require committing mutable deployment state into the repository.

## 7. Secrets and local environment

Secrets, private keys, tokens, passwords, and machine-specific secret-bearing values must not be committed.

Preferred pattern:

```text
tracked:
  .env.example or application-specific template

untracked:
  $MACHINE_SOUL/scratch/env/...
```

Shell/configuration files may reference environment variables or ignored local env files.

A single global `.env` is not mandatory. Scope local env data according to the application/host need rather than creating one giant secret namespace prematurely.

## 8. Destination state vocabulary

Check must classify each managed destination meaningfully.

Minimum states:

- `APPLIED` — destination is the expected symlink to the currently resolved tracked source;
- `NOT_APPLIED` — destination does not exist;
- `CONFLICT` — destination exists as unmanaged state that would need preservation/replacement;
- `WRONG_TARGET` — destination is a symlink but not to the expected source;
- `BROKEN` — destination is a symlink whose target does not exist;
- `UNSUPPORTED` — no source/destination mapping exists for this host/account/platform;
- `ERROR` — state could not be determined safely.

Application-specific sub-status may be added, but these names form the shared structural contract.

Structural state and Machine-Soul ownership are reported separately. A destination can be exactly linked to the expected tracked source while lacking Machine-Soul deployment metadata, so structural `APPLIED` does not by itself prove ownership.

Current ownership-state vocabulary includes:

- `managed` — recorded Machine-Soul state agrees with the exact current managed link;
- `unrecorded` — no deployment state exists for the destination;
- `managed_stale_link` — recorded state explains a wrong/broken link to the previous checkout target, such as repository relocation;
- `stale_state` — deployment state exists but no longer describes the current destination object;
- `state_conflict` — the stored record itself does not match the current application/host/account/destination/source relationship.

`check_config` is read-only. It may report a repairable stale managed link, but only a mutating operation such as Apply may repair it after performing the safety checks required by the deployment contract.

## 9. Runtime discovery and host-specific configuration

Portable environmental facts should be discovered centrally by shared runtime/library code rather than repeated as application-specific string comparisons or stored in a tracked machine registry.

Host-specific configuration remains declarative in the configuration tree itself. A host name matters only when it selects genuinely different canonical configuration.

The intended direction is:

```text
runtime-discovered host/platform/account
   + application declaration
        ↓
resolved tracked source
   + native destination
        ↓
shared deployment engine
```

Do not add a central `hosts/*.env` inventory merely to record facts the runtime can discover. Secrets or genuinely non-discoverable local values belong in ignored machine-local state, not in tracked host records.
