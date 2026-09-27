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

## 2. Paired taxonomy

Canonical configuration and the machinery that applies it are deliberately separated:

```text
assimilation_directives/
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

annexation_procedures/
└── <application>/
    ├── windows/
    └── linux/
```

`assimilation_directives/` is the repository's configuration-content tree: the equivalent of a conventional top-level `config/` tree.

`annexation_procedures/` is the operational tree: the equivalent of a conventional top-level `operations/` tree.

The two are intrinsically paired by application name, but neither is nested inside the other.

Shared symlink/backup/state/dispatch implementation belongs under `accumulated_instruments/configuration_deployment/` rather than being duplicated in each annexation procedure.

## 3. Configuration identity dimensions

A configuration may vary by:

1. application;
2. host;
3. operating platform/environment;
4. account/user;
5. optional application-specific variant where a real need appears.

Host and account are first-class dimensions. Platform normally follows from host metadata rather than being repeated in every path.

Initial host identities:

- `spaceship` — Windows workstation;
- `workhorse` — Ubuntu/Linux server;
- `runar` — Ubuntu-like server.

Initial Linux account identities include `m-a-x-i-n` and `root` where relevant.

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

Application-specific sub-status may be added, but these names form the shared contract.

## 9. Declarative host knowledge

Host/platform/account facts should be declared centrally rather than spread as string comparisons through application scripts.

Annexation procedures consume that identity data and resolve the appropriate complete assimilation directive.

The intended direction is:

```text
host inventory
   + current account
   + application mapping
        ↓
resolved tracked source
   + native destination
        ↓
shared deployment primitive
```
