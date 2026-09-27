# Stable experimental v2 baseline

## Status

The first stable `experimental/v2` baseline has been established.

This note records the repository state and validation expectations at baseline completion. It is not permission to promote or merge the branch to `main`.

## Recovery checkpoint

The chat/tool interruption during final cleanup was recovered using repository state as authority.

Verified recovery facts:

- the intended executable-mode normalization had landed as commit `938acd521dde1132d63e0f15b7e74e6e07840068`;
- subsequent additive cleanup commits removed only redundant `.gitkeep` files from directories that had gained real tracked content;
- `experimental/v1` remains preserved at `a988a05343fee1c2e0805eca43925d385f2f3805`;
- `main` remains at the clean restart commit `56206d50186583a9b9714d6811bc7ca2e998ae5d`;
- no history rewrite or forced ref movement was used.

## Baseline validation

Before marking V2-40 complete, the current v2 tree was checked for:

- all roadmap tasks V2-01 through V2-39 complete;
- no tracked content under `scratch/`;
- no `.sh` files missing executable mode;
- required architecture/support/session/extension documentation present;
- preserved empty v1 taxonomy directories retained intentionally;
- current `experimental/v2` GitHub Actions run green on the recovered head.

CI coverage at baseline includes:

- Windows and Linux shared symlink lifecycle;
- backup/restore and conflict safety;
- prompt decline and external mutation protection;
- application Apply/Unapply/Check wrappers;
- CMD registry AutoRun preservation/restore;
- managed installation dry-run/provenance behavior;
- repository relocation with restore-lineage preservation;
- fresh-clone validation on Windows and Ubuntu;
- sudo/root and remote-like process boundaries;
- multiple Linux host variants × normal/privileged account configuration resolution;
- Windows POSIX-shell path translation through `cygpath` plus the Windows PowerShell symlink runtime.

## Stable design laws

- tracked files are canonical configuration;
- native config paths are connected by file-level symbolic links;
- `$MACHINE_SOUL` is the checkout-root identity;
- mutable machine-local state lives under ignored `scratch/`;
- existing unmanaged config is preserved before replacement;
- Unapply mutates only understood owned state and restores prior state when safe;
- installation ownership is separate from configuration ownership;
- expensive-to-rediscover technical knowledge belongs in `.agents/`.

## After this checkpoint

At that baseline, the then-current task ledger had no next v2 implementation task after V2-40. Further work was expected to begin from newly authorized work or explicit user direction.

Do not merge or promote `experimental/v2` to `main` merely because this baseline is stable.