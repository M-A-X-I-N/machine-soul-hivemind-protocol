# npm annexation investigation

Status: completed research output for `MSHP-DEV-A-100`.

Research date: 2026-09-28.

## Core conclusion

npm package state is not one machine-global inventory.

A useful Machine-Soul identity is conceptually:

```text
Node runtime/backend identity
+ npm global/local prefix identity
+ package desired-root inventory
```

For project-local dependencies, the project itself normally owns the environment through `package.json` and its lockfile. For machine-level CLI tools, an explicitly managed npm global prefix can be a valid package environment.

## npm and Node are related but separate state

Node distributions normally include npm, and npm's own documentation describes Node installers/version managers as installing Node.js and npm together.

Sources:

- https://docs.npmjs.com/downloading-and-installing-node-js-and-npm/
- https://nodejs.org/en/download/archive/

The exact bundled npm version varies by Node release. At research time, for example, current Node 26 releases ship npm 11.x.

npm can also upgrade itself with npm. Therefore these are separate facts:

- Node runtime version;
- npm CLI version available for that runtime;
- global packages managed by that npm instance/prefix.

Machine-Soul should not assume one npm version globally follows from “Node is installed.”

## Global prefix is the environment boundary

npm global mode (`-g` / `--global`) installs into npm's configured global `prefix`.

On Windows, npm documentation describes global packages beneath the prefix's `node_modules` and command shims directly in the prefix.

Sources:

- https://docs.npmjs.com/files/folders/
- https://docs.npmjs.com/cli/npm-prefix/
- https://docs.npmjs.com/cli/npm-root/

Deterministic discovery must query the active npm/backend rather than hard-code a path:

```text
npm prefix -g
npm root -g
npm config get prefix
```

A user may override the prefix, and version managers can introduce their own routing/storage semantics.

Therefore “global npm package” means **global to this npm prefix/backend context**, not global to Windows.

## Direct Node installation

With a conventional Windows Node installer, npm's documented Windows global prefix defaults to a user location such as `%AppData%\npm`.

That can make global CLI packages appear user-wide across ordinary Node installer upgrades, but Machine-Soul still should discover the actual prefix rather than encode that layout as identity.

Source:

- https://docs.npmjs.com/files/folders/

This direct-install model is materially different from manager-backed Node where package state can be associated with managed runtime versions.

## nvm-windows v2

nvm-windows v2 explicitly treats global modules as version-manager-managed state.

Current documentation supports:

- lightweight shims for Node, npm, npx and related commands;
- multiple Node versions;
- optional default global modules installed with each new Node version;
- copying/installing global modules from another managed Node version;
- removal of managed Node versions and their global modules when the manager itself is uninstalled.

Sources:

- https://docs.nvm-windows.com/features/newv2/
- https://docs.nvm-windows.com/command/install/
- https://docs.nvm-windows.com/install/uninstall/

This proves that global npm inventory can be **runtime/backend-coupled**.

A Node-manager backend may legitimately expose a policy such as “these CLI modules should exist for every newly installed managed Node version,” but that is backend-specific behavior layered on top of a shared desired inventory concept.

## Other Node managers

fnm, Volta, mise, and other Node managers have different prefix/tool ownership semantics.

Volta in particular intentionally owns global JavaScript CLI tools as part of its toolchain model, so using ordinary `npm install -g` as the only abstraction would throw away useful backend semantics.

Machine-Soul should therefore ask the selected Node backend for the package environment/global-prefix identity and mutation strategy rather than assume all managers behave like direct Node.

## Inventory

Useful deterministic interfaces include:

```text
npm ls -g --depth=0 --json
npm prefix -g
npm root -g
npm config get prefix
```

Source:

- https://docs.npmjs.com/commands/npm-ls/

`npm ls -g --depth=0 --json` is a good observed top-level global inventory, but it is not durable ownership provenance by itself.

Machine-Soul must retain declared desired roots independently because:

- a top-level package may have been installed by the user outside Machine-Soul;
- manager bootstrap/default-module behavior can add packages;
- npm itself may appear in or alongside runtime-managed package state;
- manager migration/copy operations can reproduce packages without proving Machine-Soul ownership.

## Install and uninstall

The basic global lifecycle is:

```text
npm install -g <package-spec>
npm uninstall -g <package>
```

Sources:

- https://docs.npmjs.com/downloading-and-installing-packages-globally/
- https://docs.npmjs.com/uninstalling-packages-and-dependencies/

For Machine-Soul-managed state, invoke these only after resolving the exact intended Node/backend/prefix context.

Do not run generic PATH-selected npm and then infer ownership afterward.

## Desired roots versus transitive dependencies

As with LuaRocks and pip, Machine-Soul should own a declared set of requested top-level packages and observe their dependency closure.

The physical `node_modules` tree and `npm ls --all` output are not desired-state manifests.

For a global CLI inventory, desired roots might conceptually be:

```text
typescript@...
eslint@...
prettier@...
```

while their nested dependencies are implementation state owned through npm's resolver.

Uninstall should target the desired top-level package through npm and then rediscover the environment rather than deleting dependency directories manually.

## Project-local dependencies

Local npm install behavior is project-root based. npm finds/uses the package root and installs into local `node_modules`; `package.json` and lockfiles describe project dependency intent.

Source:

- https://docs.npmjs.com/downloading-and-installing-packages-locally/

These are project-owned assets by default.

Machine-Soul should **not**:

- scan repositories and convert package.json dependencies into machine-global desired state;
- own arbitrary project `node_modules`;
- rewrite project lockfiles as part of machine annexation.

A future explicit “construct this project environment” capability could delegate to the project's own manifest/lockfile, but that is distinct from global machine state.

## Corepack and alternative package managers

The earlier Node investigation established that Corepack is no longer bundled starting with Node 25 and therefore must not be assumed to accompany every Node runtime.

That keeps these state domains separate:

- Node runtime;
- npm CLI;
- optional Corepack;
- Yarn/pnpm or other package-manager shims;
- packages managed by each tool.

Do not use npm annexation as a backdoor to claim Yarn/pnpm project environments.

## Manager switching

Changing Node backends is a migration, not an in-place relabeling.

Example:

```text
nvm-windows Node 24 + global CLI packages
        ↓ migration
fnm Node 24 + a different prefix/environment
```

Even when runtime versions match, the global package environment can differ.

Migration must:

1. discover old desired/owned roots;
2. establish target backend/runtime/prefix;
3. install desired roots through the new backend/environment;
4. verify them;
5. retire old owned state only after successful migration.

Never mark old global modules as owned by a new manager merely because package names/versions match.

## npm configuration and secrets

npm configuration can live in project, user, global-prefix, and built-in npmrc layers.

Authentication fields such as `_auth`, `_authToken`, username and password are registry-scoped and can be written to `.npmrc`.

Sources:

- https://docs.npmjs.com/cli/v11/using-npm/config/
- https://docs.npmjs.com/cli/v8/configuring-npm/npmrc/
- https://docs.npmjs.com/using-private-packages-in-a-ci-cd-workflow/

Machine-Soul must never store actual registry tokens/passwords in tracked desired-state files.

Non-secret configuration such as registry/scope mappings may be portable, but token material should come from environment variables, credential stores, CI secret storage, or other machine-local secret mechanisms.

npm explicitly documents checking in a project `.npmrc` that references `${NPM_TOKEN}` rather than embedding the token itself; that pattern reinforces the desired separation.

## Native build/toolchain coupling

npm package installation can invoke lifecycle/build scripts and native-addon toolchains.

For Windows, native addons commonly depend on a compatible Node ABI/N-API/toolchain plus Python and MSVC/Build Tools depending on the package/build stack.

This means global CLI package reconciliation may fail because of external build prerequisites.

As with LuaRocks/pip, Machine-Soul should surface those prerequisites rather than silently annex arbitrary native toolchains as a package side effect.

The already identified MSVC/Build Tools investigation is therefore relevant to npm too.

## Safe initial Machine-Soul boundary

An initial npm package capability can reasonably support:

1. npm availability/version discovery per exact managed Node runtime/backend;
2. an explicitly selected **global CLI package environment** keyed by Node/backend/global-prefix identity;
3. declared desired top-level global packages;
4. machine-readable discovery and npm-native install/uninstall;
5. backend-native global-module policy where the chosen manager exposes one;
6. secrets excluded from tracked state.

It should leave project-local dependencies under project ownership by default.

## Scenario walkthrough

### Direct Node

Node is installed directly. Machine-Soul resolves the actual global npm prefix, adopts it only if explicitly selected, and manages declared CLI roots there.

### Version-managed Node

Node 22 and Node 24 coexist under nvm-windows. Their manager semantics may associate different global-module state with each runtime. Desired packages must identify the intended runtime/backend package environment.

### Switch active Node

Changing the selected Node version must not cause Machine-Soul to reinterpret another runtime's global packages as the selected runtime's inventory. Selection changes runtime routing; package-environment provenance remains exact.

### Remove one Node version

Before removing an owned Node runtime, Machine-Soul must account for package environments owned beneath/through that runtime. Desired CLI tools may need migration/reinstallation elsewhere or explicit removal.

### Switch manager

nvm-windows → fnm/Volta/mise is a package-environment migration as well as a runtime migration. Global package provenance cannot be transferred by label.

## Conclusion

npm strongly validates the shared package-environment model:

> runtime/backend identity + environment/prefix identity + declared desired roots are separate from observed dependency closure.

Unlike pip's venv-centered isolation or LuaRocks' explicit tree model, npm's most useful machine-level target is the **explicit global CLI prefix attached to a known Node/backend context**.

That is manageable, but `npm -g` must never be interpreted as one universal machine-global scope.
