# Lua multiversion annexation investigation

Status: completed research output for `MSHP-DEV-A-030`.

Research date: 2026-09-28.

## Scope update

The task originally named Lua 5.1 through 5.4. Lua 5.5 is now a current released line, so the investigation includes maintained PUC Lua 5.1, 5.2, 5.3, 5.4, 5.5 and LuaJIT where relevant.

Official Lua release history currently lists:

- Lua 5.1.5;
- Lua 5.2.4;
- Lua 5.3.6;
- Lua 5.4.9;
- Lua 5.5.1.

Sources:
- https://www.lua.org/versions.html
- https://www.lua.org/ftp/

## The ecosystem problem

There is no single obvious current native-Windows manager that cleanly owns PUC Lua 5.1 through 5.5 plus LuaJIT while also providing deterministic side-by-side version identity, default selection, discovery, and exact uninstall.

That does not make multiversion annexation impractical. It means Machine-Soul should separate two ideas:

1. **installed runtime instances** — exact version/flavor/architecture/prefix;
2. **selected/default command** — which installed instance owns generic `lua` / `luac` resolution.

Those concepts must not be collapsed into package installation order or ambient PATH precedence.

## Official source and LuaBinaries

Lua itself primarily distributes source. The Lua FAQ/download guidance points users wanting prebuilt Windows binaries toward LuaBinaries.

LuaBinaries provides Windows x86/x64 archives and deliberately uses version-qualified executable/library names. For example, Lua 5.4 uses names such as `lua54.exe` / `lua54.dll`, and current 5.5 builds similarly use `lua55` naming.

Sources:
- https://www.lua.org/download.html
- https://luabinaries.sourceforge.net/download.html
- https://luabinaries.sourceforge.net/configuration.html

This naming is inherently friendly to side-by-side installation. Multiple runtime versions can live in distinct prefixes while retaining deterministic versioned commands.

Tradeoff: LuaBinaries can lag the newest upstream patch release. At research time the official Lua lines were newer than some available LuaBinaries/Scoop packages. If patch-currentness matters, source builds become relevant.

## Scoop

Scoop is a credible Windows acquisition layer but is not, by itself, a perfect Lua multiversion semantic model.

Current `ScoopInstaller/Main`:

- `lua` tracks the current LuaBinaries release and exposes the version-qualified executable plus generic `lua` / `luac` aliases;
- `luajit` currently consumes an MSYS2 package;
- `luarocks` depends on Scoop's selected `lua` and writes configuration bound to that runtime.

`ScoopInstaller/Versions` currently provides separate apps for older Lua lines:

- `lua51` — Lua 5.1.5;
- `lua52` — Lua 5.2.4;
- `lua53` — Lua 5.3.6;
- `lua54` — Lua 5.4.x.

The 5.1/5.2 manifests also request generic `lua`/`luac` shims, while 5.3/5.4 expose version-qualified executables. The current main `lua` app also owns generic aliases.

Sources:
- https://github.com/ScoopInstaller/Main/blob/master/bucket/lua.json
- https://github.com/ScoopInstaller/Main/blob/master/bucket/luajit.json
- https://github.com/ScoopInstaller/Main/blob/master/bucket/luarocks.json
- https://github.com/ScoopInstaller/Versions/blob/master/bucket/lua51.json
- https://github.com/ScoopInstaller/Versions/blob/master/bucket/lua52.json
- https://github.com/ScoopInstaller/Versions/blob/master/bucket/lua53.json
- https://github.com/ScoopInstaller/Versions/blob/master/bucket/lua54.json

Scoop supports installed-version switching generally, but Lua's split across distinct app names plus overlapping generic shims means Machine-Soul should not let Scoop install order implicitly define the default Lua.

A future Scoop-backed implementation could still use Scoop for acquisition while Machine-Soul separately owns the selected/default alias.

## Hererocks

Hererocks has an attractive conceptual model: each isolated prefix can contain one Lua/LuaJIT runtime plus its own LuaRocks installation, with prefix-local `lua`/`luarocks` executables.

However, its published version support/documentation is materially stale relative to current Lua/LuaJIT releases. It should therefore not be selected as Machine-Soul's default Windows backend merely because its isolation model is elegant.

Source: https://github.com/luarocks/hererocks

## luaenv

`luaenv` follows the rbenv-style shim/version-selection model and is conceptually relevant, but the implementation/setup is POSIX-shell oriented. The investigation found no trustworthy native-Windows lifecycle suitable for Machine-Soul's Windows target.

Source: https://github.com/cehoffman/luaenv

## mise / vfox

`mise` itself is current and supports Windows, but Windows cannot use legacy asdf plugins directly. Its current Lua registry entry prefers the vfox plugin `mise-plugins/vfox-lua`.

That plugin explicitly documents support for Linux and macOS, compiles Lua from source with `make`, and does not currently provide native Windows support.

Sources:
- https://mise.jdx.dev/troubleshooting.html
- https://github.com/jdx/mise/blob/main/registry/lua.toml
- https://github.com/mise-plugins/vfox-lua

Therefore `mise use lua@...` is not currently a complete answer to native-Windows Lua multiversion annexation.

The LuaJIT registry path has different backends, which reinforces that Lua and LuaJIT cannot be assumed to share one manager implementation.

## LuaJIT

LuaJIT 2.1 uses a rolling-release model. Upstream distributes source and explicitly discourages random third-party pseudo-releases/binaries; trusted OS/package-manager builds are acceptable but may lag.

Official Windows build support includes x86/x64 and ARM64 using MSVC or MinGW toolchains.

Sources:
- https://luajit.org/download.html
- https://luajit.org/install.html
- https://luajit.org/status.html

LuaJIT should be modeled as a separate runtime **flavor**, not merely labeled 'Lua 5.1'. It is largely Lua-5.1-compatible but has its own identity, versioning, ABI/runtime behavior, executable name, and installation source.

## LuaRocks binding preview

Detailed LuaRocks ownership belongs to `MSHP-DEV-A-080`, but current LuaRocks Windows installation already proves that explicit per-runtime binding is feasible.

Its Windows installer supports selecting Lua version/path/bindings and current installer logic recognizes multiple version-qualified executable names. That supports a future model where each managed Lua runtime has a separately addressable package environment/tree.

Source: https://github.com/luarocks/luarocks

Do not make a single ambient LuaRocks installation implicitly follow whichever generic `lua` happens to win PATH.

## Candidate implementation directions

### A. Machine-Soul-owned versioned prefixes

Machine-Soul could acquire/build each desired runtime into an exact private/user-scoped prefix, exposing version-qualified commands and keeping generic alias selection separate.

Advantages:

- exact ownership and uninstall;
- deterministic coexistence;
- independent patch versions;
- no dependency on one version manager's lifecycle;
- can use LuaBinaries when acceptable and build from source when necessary.

Costs:

- Machine-Soul becomes responsible for archive/build acquisition logic;
- source builds require compiler/toolchain handling;
- update-source policy and checksums become Machine-Soul concerns.

### B. Delegate acquisition to Scoop, own selection separately

Use current/versioned Scoop packages as acquisition identities while Machine-Soul records exact installed instances and owns the generic default alias/shim independently.

Advantages:

- mature Windows package acquisition/uninstall;
- existing manifests/checksums;
- simpler install mechanics.

Costs:

- current/older Lua lines are split across app identities;
- generic shim collisions need careful control;
- package patch availability can lag upstream;
- LuaJIT comes from a different substrate.

### C. Delegate everything to a version manager

This would be ideal if a maintained native-Windows manager covered all desired Lua versions/flavors with exact install/list/select/uninstall semantics.

The investigation did not find one sufficiently complete/current to recommend today. Keep this option open for future ecosystem changes.

## Discovery

Discovery must enumerate exact managed runtime instances rather than ask only `where lua`.

For each candidate preserve at least:

- flavor (`lua` or `luajit`);
- semantic runtime version;
- architecture;
- backend/source identity;
- installation prefix/path;
- executable path(s);
- Machine-Soul ownership/provenance;
- whether it is currently selected as the generic/default command.

Runtime probes should execute each candidate directly. PUC Lua can expose `_VERSION` / `-v`; LuaJIT exposes its own version string. Do not infer version solely from filename or PATH.

## Default/selected runtime

The generic command is **desired state separate from the version set**.

Desired state should be able to express something conceptually like:

```text
installed:
  lua: [5.1.x, 5.2.x, 5.3.x, 5.4.x, 5.5.x]
  luajit: [2.1...]
selected:
  lua: 5.4.x
```

The exact generic model is deferred to `MSHP-DEV-A-070`; this task only establishes that installed-set and selected/default cannot be the same field.

Selection mechanisms could include a Machine-Soul-owned shim/alias directory, backend-native selection, or another proven mechanism. PATH package-install order is not acceptable policy.

## Uninstall semantics

Removing one runtime version must target exactly one owned prefix/package instance.

If the removed version currently owns the generic/default command, Machine-Soul must either:

- atomically move selection to another explicitly desired installed version; or
- refuse the uninstall until selected/default desired state is changed.

Uninstall must not delete another version's runtime, libraries, or LuaRocks tree.

## Architecture

PUC Lua Windows binaries commonly exist in x86 and x64 variants; LuaJIT also supports ARM64 upstream. Architecture is therefore part of runtime-instance identity, not merely host metadata.

The investigation does not choose the maintainer's desired architecture policy.

## Conclusion

A sane multiversion Windows Lua model is feasible, but current ecosystem tooling does not justify delegating the entire problem to one manager.

The strongest current direction to carry into cross-runtime synthesis is:

> Treat every installed runtime version/flavor as an exact managed instance, prefer naturally version-qualified executables/prefixes, and manage selected/default command resolution separately from the installed version set.

Whether acquisition should be direct LuaBinaries/source-build, Scoop-backed, or generalized through future runtime-manager machinery should be decided only after the Python and Node investigations.
