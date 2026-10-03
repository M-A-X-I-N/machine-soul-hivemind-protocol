# MSHP-DEV-B-080 — Implement pip and npm package backends

## Description

Implement two deliberately different package-environment backends—pip and npm—to validate the shared package-environment core against interpreter/venv semantics and Node/global-prefix semantics.

## Requirements

### pip

- Bind every operation to an exact Python environment/interpreter, preferring exact `python -m pip` invocation over PATH-selected pip.
- Discover packages using current machine-readable pip interfaces and preserve direct/source metadata where materially needed.
- Respect `EXTERNALLY-MANAGED` environments as read-only under normal reconciliation.
- Support explicitly adopted/owned environments only; do not auto-own arbitrary project venvs or user-site state.
- Reconcile declared desired roots through pip-native install/uninstall and rediscover afterward.
- Distinguish environment-local packages from inherited visibility such as system-site-packages.

### npm

- Resolve exact Node/backend/global-prefix identity before inventory or mutation.
- Discover top-level global package state using npm's machine-readable interfaces.
- Reconcile explicitly desired global CLI roots through npm-native install/uninstall.
- Preserve nvm-windows/runtime-specific global-prefix semantics; do not interpret `-g` as machine-global.
- Leave project `package.json`, lockfiles, and local `node_modules` project-owned.

### Both

- Keep package-manager tool version/state separate from desired package roots.
- Never persist registry/index credentials or secrets.
- Surface missing native-build prerequisites instead of silently installing toolchains.
- Add tests with unmanaged roots/transitives and runtime-bound environment migration/removal checks.

## Constraints / non-goals

- Do not implement pipx, Poetry, uv, Yarn, pnpm, or Corepack merely for completeness.
- Do not manage project-local dependencies.
- Do not use pip external-ownership override flags as normal policy.
- Do not mutate unknown/unowned top-level packages by default.

## Acceptance criteria

- pip and npm both implement the shared environment contract without requiring shared command syntax.
- Exact runtime/environment identity drives every mutation.
- Desired roots remain distinct from observed/transitive packages.
- Project/external ownership and secrets boundaries are enforced.

## Validation

- Use current pip/PyPA/npm/Node docs where command contracts may have changed.
- Test Python venv/read-only/user-like cases and Node multi-version/global-prefix cases.
- Run the repository Python validation suite.
