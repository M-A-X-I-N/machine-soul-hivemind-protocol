# MSHP-DEV-B-050 — Implement Node multiversion backend

## Description

Implement Windows Node.js multiversion annexation using current nvm-windows v2 Community behavior as the initial backend while preserving the shared backend boundary for future alternatives such as fnm or Volta.

## Requirements

- Manage/discover nvm-windows itself separately from Node runtime instances.
- Target current v2 semantics and documentation; do not encode legacy nvm-windows 1.x behavior.
- Support multiple exact installed Node versions with backend-native inventory, install, use/default selection, and exact uninstall.
- Model nvm-windows shim/link selection details behind the backend rather than in shared runtime core.
- Preserve project-local version selectors such as `.nvmrc`, `.node-version`, or package metadata as project-owned state.
- Discover bundled npm identity/version as runtime-adjacent observed state without annexing npm packages yet.
- Keep Corepack separate because current Node releases no longer guarantee it is bundled.
- Refuse implicit manager migration/adoption; another manager's Node installations remain unmanaged candidates until an explicit future migration.
- Add fake-runner/unit coverage for several versions, selected/default changes, shim/link observations, exact uninstall, and unmanaged Node candidates.

## Constraints / non-goals

- Do not manage global npm packages in this task.
- Do not implement fnm/Volta/mise as additional backends merely for completeness.
- Do not claim project version files.
- Do not copy/auto-install global npm modules as a side effect unless explicitly required for runtime-manager correctness.

## Acceptance criteria

- Machine-Soul can safely own several nvm-windows v2 Node runtimes and selected/default state.
- Runtime identity remains exact across switching and uninstall.
- npm/Corepack/package-tool state is not conflated with Node runtime ownership.
- The backend remains replaceable without contaminating shared runtime semantics.

## Validation

- Re-check current nvm-windows v2 command/output contracts during implementation.
- Exercise multi-version install/discovery/selection/removal through the fake command boundary.
- Run the repository Python validation suite.
