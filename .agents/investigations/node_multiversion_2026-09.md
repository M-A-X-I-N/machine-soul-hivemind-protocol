# Node multiversion annexation findings

Durable findings from `MSHP-DEV-A-050` (2026-09-28):

- Current Node release cadence makes multiversion practical: v26 Current, v24/v22 LTS at research time.
- No first-party Windows multiversion manager exists; several maintained third-party managers are credible.
- nvm-windows v2 is the leading Windows-specific candidate: current community edition is per-user/no-admin, supports multiple installed versions, exact install/uninstall, native shim/link modes, per-directory switching and auto-install/module features.
- Do not rely on legacy nvm-windows 1.x wiki behavior when evaluating v2.
- fnm is a strong cross-platform alternative, but relies on shell-specific `fnm env` setup and CMD is explicitly less completely covered.
- Volta deliberately combines Node versioning, package-manager versions and global CLI package pinning; selection would imply broader package/tool ownership.
- Corepack is no longer bundled starting with Node 25; manage it separately from Node runtime state.
- Installed version set, global/default selection, project-local selection, and runtime-bound npm/tool state are independent concepts.
- Compare nvm-windows/fnm/backend-specific management against cross-runtime mise in `DEV-A-070`; do not hardcode manager semantics into the core model.

Detailed research lives in `autonomic_affairs/tasks/archive/MSHP-DEV-A/workspace/node_multiversion.md`.