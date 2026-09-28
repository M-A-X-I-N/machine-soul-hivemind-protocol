# Scoped installation lifecycle

The current Machine-Soul managed-install lifecycle is scope-aware and candidate-exact.

Key invariants:

- scope policy (mutation intent) is distinct from observed installation scope;
- Apt is fixed MACHINE scope;
- WinGet mutation is explicitly scoped and must not inherit ambient WinGet scope preferences;
- machine provenance is host-owned; user/package-user provenance is scoped to the relevant user;
- user and machine ownership may coexist for the same application;
- ownership requires an exact matching discovery candidate, not merely package presence;
- post-install rediscovery must prove a compatible candidate before provenance is written;
- uninstall requires exact scoped provenance and candidate matching;
- legacy scope-less state is unreconciled unless a backend can prove one safe migration;
- non-current user-scoped mutation is unsupported without a proven target-user mechanism.

Deferred Flatpak/Homebrew/pipx/etc. concerns live in `autonomic_affairs/initiatives/MSHP-INST-SCOPE.md` and are not executable tasks merely because they are known.
