# MSHP-DEV-B-010 — Promote install-only developer editor annexation

## Description

Promote VS Code and JetBrains Toolbox as installation-only Machine-Soul applications using the scoped WinGet lifecycle already implemented. Keep editor configuration, profiles, plugins/extensions, IDE products, and cloud-sync ownership out of this task.

## Requirements

- Add a VS Code application declaration using WinGet identity `Microsoft.VisualStudioCode`.
- Require USER scope for the initial VS Code declaration, matching the upstream-recommended normal Windows install while leaving future machine-scope support representable.
- Add a JetBrains Toolbox application declaration using WinGet identity `JetBrains.Toolbox` with required USER scope.
- Provide the ordinary install/uninstall/check-installed entrypoints/wrappers expected by the current application model.
- Use existing native/WinGet discovery and scoped ownership machinery rather than application-specific mutation branches.
- Add declaration/discovery/operation regression tests consistent with existing managed applications.
- Update developer-environment documentation/initiative coverage to distinguish installation support from still-unselected configuration/add-on state.

## Constraints / non-goals

- Do not invent VS Code settings, keybindings, snippets, profiles, extensions, or Settings Sync policy.
- Do not invent Toolbox settings, IDE product/version selections, JetBrains plugins, or Backup and Sync policy.
- Do not depend on the experimental Toolbox CLI for IDE lifecycle.
- Do not add a generic plugin/extension abstraction in this task.

## Acceptance criteria

- VS Code and Toolbox support Install/Uninstall/CheckInstalled through normal Machine-Soul machinery.
- Both declarations enforce the researched USER scope.
- No configuration operation is falsely advertised merely because installation is supported.
- Existing application behavior and scoped installation tests remain green.

## Validation

- Run the Python/unit validation suite used for application declarations and scoped WinGet lifecycle.
- Verify declaration metadata and package identities against the completed DEV-A investigation output.
- Confirm no editor config/plugin desired content was introduced.
