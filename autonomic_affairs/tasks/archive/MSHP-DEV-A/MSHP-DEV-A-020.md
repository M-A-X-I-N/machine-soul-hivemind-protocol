# MSHP-DEV-A-020 — Investigate JetBrains and Toolbox annexation

## Description

Investigate JetBrains Toolbox and the JetBrains IDE ecosystem as one ownership/version-management domain before deciding whether Machine-Soul should manage Toolbox, individual IDEs, or both.

## Requirements

- Research current Toolbox installation, product/version lifecycle, update channels, discovery, uninstall, and any supported CLI/native automation.
- Map how Toolbox-managed IDE versions coexist and how ownership differs from direct IDE installations.
- Investigate user settings/configuration, plugins, keymaps, code styles, inspections, SDK/toolchain references, and project-local versus global state.
- Investigate JetBrains Settings Sync/account-backed synchronization and coexistence boundaries with Machine-Soul.
- Determine whether common IDE state can be represented once with product-specific overlays.
- Use Rider as a concrete representative and compare at least one other IDE shape before generalizing.
- Identify licenses/account state, credentials, caches, indexes, machine paths, generated state, and other content that must remain outside assimilation directives.
- Separate Toolbox installation/version management from IDE configuration/plugin management.
- Classify implementation-ready capabilities versus gaps requiring desired content or additional design.

## Constraints / non-goals

- Do not install Toolbox or IDEs.
- Do not log in to JetBrains services or alter Settings Sync.
- Do not copy system/cache/index directories into Git.
- Do not pre-decide that Toolbox must be the installation backend.
- Do not let Rider-specific behavior define the whole ecosystem without comparison.

## Acceptance criteria

- The Toolbox-versus-IDE ownership boundary is explicit.
- Multiversion IDE coexistence/update-channel behavior is understood.
- Common versus product-specific configuration/plugin surfaces are mapped.
- Installation support can be designed independently from configuration support.

## Validation

- Use current official JetBrains documentation/upstream tooling.
- Compare Toolbox, Rider, and at least one other IDE family member.
- Record expensive-to-rediscover paths, interfaces, and rejected state surfaces.
