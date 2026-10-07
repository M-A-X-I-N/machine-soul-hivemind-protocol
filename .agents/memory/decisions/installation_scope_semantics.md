# Installation scope semantics

Machine-Soul installation scope is independent from target account, execution identity, and Machine-Soul ownership.

Durable decisions from `MSHP-INST-A-010`:

- keep discovery-side `InstallationScope` as observed actual state;
- mutation uses a separate scope contract;
- current required semantic modes are fixed scope, required explicit scope, and intentionally delegated scope;
- package-manager defaults/preferences must never accidentally substitute for a fixed/required Machine-Soul scope;
- user-scoped mutation for a non-current target account is unsupported unless a backend provides a proven target-user/impersonation mechanism;
- machine-scoped provenance belongs to the host/machine rather than an arbitrary requesting account;
- legacy scope-less install provenance is unknown/unreconciled until safely matched;
- uninstall must match exact scope/subject/native identity and refuse ambiguity;
- post-install ownership should be recorded only after actual scope is compatible with the strategy contract.

The human-facing canonical semantics are `meta/docs/INSTALLATION_SCOPE.md`.
