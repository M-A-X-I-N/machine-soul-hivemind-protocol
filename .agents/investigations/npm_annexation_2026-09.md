# npm annexation findings

Durable findings from `MSHP-DEV-A-100` (2026-09-28):

- Node normally ships with npm, but Node version, npm CLI version, and npm-managed package inventory are separate state.
- npm global mode is scoped to the active global `prefix`; on Windows, global packages live under that prefix. Always discover `npm prefix -g` / `npm root -g` rather than treating `-g` as a universal machine scope.
- Node version managers can bind global modules to managed Node versions. nvm-windows v2 can auto-install/copy global modules per Node version and removes managed global modules with its managed installs.
- A safe global package-environment identity includes exact Node runtime/backend plus exact npm global prefix.
- `npm ls -g --depth=0 --json` is useful observed inventory, but declared desired roots must remain separate from discovery/provenance and transitive dependency closure.
- Project-local `package.json`, lockfiles, and `node_modules` remain project-owned by default.
- npm, Corepack, alternative package-manager shims, and their managed packages are distinct ownership subjects.
- Switching Node managers is also a package-environment migration; do not relabel global packages as owned by the target backend.
- npmrc can contain registry auth tokens/passwords. Keep credentials outside tracked Machine-Soul state; portable config may reference external secret variables/providers instead.
- Native npm packages may require Python/MSVC/other build prerequisites; report missing prerequisites rather than silently annexing them.
- An initial useful npm capability may manage explicitly selected global CLI inventories bound to exact Node/backend/prefix environments while leaving project dependencies alone.

Detailed research lives in `autonomic_affairs/agent_tasks/MSHP-DEV-A/workspace/npm.md`.
