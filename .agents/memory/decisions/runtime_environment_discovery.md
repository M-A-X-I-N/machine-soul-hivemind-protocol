# Runtime environment discovery

## Verified during V2-48

The former top-level `hosts/` directory contained only three `.env` records plus explanatory documentation.

A repository-wide scan of the active `experimental/v2` tree found:

- `MACHINE_SOUL_PLATFORM` only in those host records;
- `MACHINE_SOUL_OS_FAMILY` only in those host records;
- `MACHINE_SOUL_ACCOUNTS` only in those host records;
- no runtime consumer of `hosts/spaceship.env`, `hosts/workhorse.env`, or `hosts/runar.env`;
- the only non-inventory reference requiring correction was the old extension instruction to create `hosts/<hostname>.env`.

Therefore the tracked host inventory was dead metadata, not an implementation dependency.

## Rule

Discover portable host/platform/account facts at runtime whenever practical. Retain explicit environment overrides for tests and unusual environments, but do not make normal execution depend on a tracked host registry.

Host-specific paths under `assimilation_directives/<application>/hosts/<hostname>/` remain valid because they represent actual configuration variants rather than inventory metadata.

Account existence or configuration availability does not imply that the account is managed; explicit account-targeting rules are handled separately.
