# MSHP-DEV-A-010 — Investigate VS Code annexation

## Description

Investigate VS Code as a Machine-Soul annexation subject. Installation, configuration, profiles, extensions, and synchronization are separate capabilities; none implies ownership of the others.

## Requirements

- Use current official Microsoft/VS Code documentation and authoritative upstream behavior where practical.
- Investigate Windows installation mechanisms, scope, stable package identities, update behavior, discovery, and uninstall.
- Map user configuration surfaces including settings, keybindings, snippets, profiles, and relevant machine-specific/user-specific files.
- Investigate extension inventory/install/uninstall interfaces and whether extensions should be modeled as application plugins/packages rather than ordinary config.
- Investigate VS Code Profiles and their interaction with settings, extensions, and snippets.
- Investigate Settings Sync and define safe coexistence/ownership boundaries if Machine-Soul also manages local desired state.
- Identify secrets, authentication state, caches, workspace history, machine IDs, session state, and other content that must not be tracked.
- Assess Apply/Check/Verify feasibility independently from Install/CheckInstalled/Uninstall.
- Classify implementation-ready capabilities, capabilities requiring canonical desired content, and structured deferred gaps.

## Constraints / non-goals

- Do not invent the maintainer's VS Code settings, profiles, keybindings, or extension list.
- Do not enable/disable Settings Sync.
- Do not install/uninstall VS Code or extensions.
- Do not assume every VS Code data file belongs in assimilation_directives.

## Acceptance criteria

- A sourced map exists for install lifecycle, configuration, profiles, extensions, and sync.
- Machine-Soul versus Settings Sync ownership boundaries are explicit.
- Install-only support remains viable even if no assimilation directives are chosen.
- Promotable implementation work and initiative gaps are clearly separated.

## Validation

- Cross-check current repo support before proposing additions.
- Verify paths/interfaces against current official docs/upstream.
- Review proposed tracked state for secrets/generated/session content.
- Preserve expensive findings in task workspace and durable memory as appropriate.
