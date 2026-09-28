# Node multiversion annexation investigation

Status: completed research output for `MSHP-DEV-A-050`.

Research date: 2026-09-28.

## Current Node release context

At research time Node.js v26 is Current, while v24 (Krypton) and v22 (Jod) are LTS lines. Older v20 is already EOL.

Sources:
- https://nodejs.org/en/about/previous-releases
- https://nodejs.org/en/blog/release

Node's relatively fast lifecycle makes multiversion support a practical requirement rather than an edge case.

## Official Node distribution

Node.js publishes official Windows binaries/installers for each release, but does not itself provide a first-party Windows multiversion manager comparable to Python's 2026 Python Install Manager.

Consequently, a sane Machine-Soul Windows lifecycle should either:

- delegate runtime versions to a maintained version manager; or
- own exact Node distribution prefixes/shims itself.

The current ecosystem is strong enough that direct Machine-Soul archive management is not the leading option.

## nvm-windows v2

Modern NVM for Windows v2 is materially different from the legacy 1.x behavior many older guides describe.

Current community-edition capabilities include:

- per-user installation without mandatory admin;
- native shim mode with no symlink requirement, plus link mode;
- multiple simultaneous installed Node versions;
- `nvm install <version>...` for one or more versions;
- exact `nvm uninstall <version>...`;
- `nvm use <version>` for selected/default version;
- per-directory version switching/pinning;
- optional automatic installation of missing versions;
- automatic/default global module facilities;
- Windows registry/Apps integration;
- local/air-gapped source support.

Current per-user storage defaults under `%LOCALAPPDATA%\Author Software\nvm`, with managed runtimes beneath the configured install root.

Sources:
- https://github.com/nvm-windows/nvm
- https://docs.nvm-windows.com/command/install/
- https://docs.nvm-windows.com/command/use/
- https://docs.nvm-windows.com/command/uninstall/
- https://docs.nvm-windows.com/install/uninstall/

This is currently the strongest **Windows-specific traditional Node version-manager** candidate for Machine-Soul.

### Important v2 distinction

Old nvm-windows 1.x wiki pages are now explicitly labeled legacy. Use the current `docs.nvm-windows.com` documentation for implementation decisions.

Legacy documentation stating NVM4W is not designed for multiple active versions describes old behavior and should not be used to characterize v2's shim/per-directory features.

### Package-manager coupling

nvm-windows installs Node distributions that include their matching npm. Global npm modules are associated with runtime installs, and v2 exposes copy/default module features when installing versions.

This means runtime replacement/removal can affect globally installed npm tools for that runtime. `MSHP-DEV-A-100/110` must define whether such module state is desired Machine-Soul inventory or intentionally outside runtime ownership.

## fnm

`fnm` is a maintained Rust-based cross-platform Node manager with native Windows support and WinGet identity `Schniz.fnm`.

Capabilities include:

- exact/partial/LTS installs;
- architecture selection;
- multiple installed versions;
- exact uninstall;
- runtime selection;
- `.node-version` / `.nvmrc` discovery;
- optional automatic directory switching;
- `fnm env --json` and shell-specific environment generation;
- PowerShell, bash, zsh, fish support, plus partial CMD support.

Sources:
- https://github.com/Schniz/fnm
- https://github.com/Schniz/fnm/blob/master/docs/commands.md
- https://github.com/Schniz/fnm/blob/master/docs/configuration.md

fnm is attractive where one manager should behave consistently across Windows/Linux/macOS. Its main Windows tradeoff for Machine-Soul is that normal operation requires evaluating `fnm env` in each shell; CMD support is explicitly less completely covered.

Given this repository already manages multiple shell startup surfaces, that is feasible but creates more assimilation/integration coupling than nvm-windows' native shim mode.

## Volta

Volta is also Windows-native and officially recommends WinGet installation (`Volta.Volta`).

Volta uses PATH shims and combines:

- a default Node version;
- per-project Node/package-manager pinning stored in `package.json`;
- npm/Yarn package-manager versions;
- globally installed JavaScript CLI tools pinned to the Node engine used when installed.

Sources:
- https://docs.volta.sh/guide/getting-started
- https://docs.volta.sh/guide/understanding
- https://docs.volta.sh/reference/list
- https://docs.volta.sh/reference/pin

This provides excellent reproducibility for project tooling, but it is intentionally **more than a runtime manager**. Choosing Volta as Machine-Soul's Node backend would implicitly influence package-manager and global CLI-tool ownership.

That may be desirable later, but `DEV-A-100/110` should evaluate it before Machine-Soul commits to Volta.

## mise

`mise` supports multiversion Node as part of a broad cross-language tool manager and may be attractive if `DEV-A-070` concludes a shared manager should own many developer runtimes.

However, choosing mise for Node now would be an architectural decision about the entire developer environment, not merely the best Node lifecycle.

Keep it in synthesis comparison rather than selecting it in isolation.

## Selected/default versus installed set

All credible managers reinforce the same distinction already seen in Lua/Python:

- installed Node versions are a **set of runtime instances**;
- one version may be the global/default selection;
- project-local selection may override global selection.

Machine-Soul should therefore avoid representing Node desired state as one scalar `version`.

Conceptually:

```text
installed: [22.x, 24.x, 26.x]
default: 24.x
project selection: owned by project files / version manager
```

Project-specific `.nvmrc`, `.node-version`, `package.json` Volta metadata, or mise config normally belong in project repositories, not global Machine-Soul assimilation.

## Discovery

A manager-backed implementation should prefer manager-native installed-version inventory plus direct runtime probes.

For each runtime instance preserve:

- exact Node semantic version;
- architecture;
- backend/manager;
- installation/prefix identity;
- direct executable path when available;
- bundled npm version;
- Machine-Soul ownership;
- selected/default status.

`node --version` and `process.execPath` can verify direct runtime identity. Do not infer installed versions solely from whichever `node.exe` wins PATH.

## Uninstall

Exact uninstall is a first-class requirement.

nvm-windows and fnm expose version-specific uninstall. Removing the selected/default runtime must first choose/reconcile another desired default or fail rather than leave ambiguous command routing.

Package/global-tool state coupled to that runtime must be handled according to the later npm/package-environment policy.

## Corepack

Corepack must not be treated as a stable component guaranteed to accompany every Node runtime.

Node documentation states that Corepack is no longer distributed starting with Node.js v25. Users needing it must install/manage the userland Corepack package separately.

Source: https://nodejs.org/download/release/v25.8.0/docs/api/corepack.html

This means future Machine-Soul support should model Corepack (and pnpm/Yarn shims) separately from the Node runtime itself.

## Manager comparison

| Manager | Windows fit | Installed-version lifecycle | Selection model | Package/tool coupling | Main concern |
|---|---|---|---|---|---|
| nvm-windows v2 | Excellent/native | strong install/list/use/uninstall | global + per-directory/shim | npm/global modules per version | Windows-specific; v2 relatively new |
| fnm | Excellent/cross-platform | strong | shell environment + version files | optional Corepack behavior | shell startup integration, CMD less complete |
| Volta | Excellent/native | strong toolchain cache/selection | global + project package.json pinning | intentionally strong | package/tool ownership bundled into choice |
| mise | Cross-runtime | strong | global/project manager config | broad tool ecosystem | choosing it is a cross-runtime architecture decision |

## Leading direction

For a Windows-first Node implementation considered in isolation, **nvm-windows v2 is the leading backend candidate** because it is Windows-native, current, per-user, supports exact multi-version lifecycle and native shim/per-directory selection without requiring each shell to evaluate manager environment output.

fnm is the strongest lightweight cross-platform alternative.

Do not promote either to implementation until `MSHP-DEV-A-070` compares whether Machine-Soul benefits more from backend-specific runtime managers or a shared cross-runtime manager strategy.

## Conclusion

Node strongly validates the shared conceptual model:

> desired installed runtime set, global/default selection, project-local selection, and runtime-bound package/tool state are separate concerns.

Unlike Lua, Node has multiple credible managers. Unlike Python, none is first-party Node infrastructure. Machine-Soul should model the manager as a backend rather than bake nvm/fnm/Volta semantics into core runtime state.
