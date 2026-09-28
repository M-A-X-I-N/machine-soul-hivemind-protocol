# Installation scope synthesis

Status: synthesis output for `MSHP-INST-A-040`.

## Implementation shape

The evidence supports one shared core/ownership pipeline and two current backend integrations.

1. `MSHP-INST-B-010` — mutation scope policy/value model.
2. `MSHP-INST-B-020` — scope-aware provenance/state namespaces.
3. `MSHP-INST-B-030` — discovery-candidate-exact ownership/install/uninstall lifecycle.
4. `MSHP-INST-B-040` — WinGet explicit scope and dual-scope discovery/uninstall.
5. `MSHP-INST-B-050` — Apt fixed machine scope and safe legacy reconciliation.
6. `MSHP-INST-B-060` — end-to-end integration/docs/initiative closure for current coverage and resume APPS-A.

## Finding-to-task traceability

- Scope policy distinct from observed actual scope -> B-010.
- Non-current user mutation refusal -> B-010/B-030.
- Machine provenance cannot live under arbitrary account; user+machine may coexist -> B-020.
- Legacy scope-less state unsafe for uninstall -> B-020/B-030, backend-safe reconciliation in B-050 for Apt.
- Current `_is_installed` boolean cannot represent dual-scope ownership -> B-030.
- WinGet ambient preferences/defaults and unscoped list/uninstall are unsafe -> B-040.
- Current OMP AppX manifest lacks `Scope:` and needs runtime/native verification -> B-040 regression coverage.
- Apt fixed machine semantics + sudo separation -> B-050.
- Deferred Flatpak/Homebrew/pipx gaps belong in initiative rather than tasks -> B-060 initiative update.

## Why future managers are not tasks

Flatpak, Homebrew/Linuxbrew, pipx, Snap/Nix and other managers are not current Machine-Soul mutation backends. Their research served as abstraction tests. Creating implementation tasks now would violate the initiative/task boundary just established.

## Windows config candidate scheduling

`MSHP-APPS-A-010` remains structurally independent. It should resume after B-060 because WinGet settings are one of its seeded candidates and current unscoped WinGet mutation would allow those settings to alter Machine-Soul behavior. Once B-060 proves explicit scope, the investigation is safe to continue without a false dependency edge.
