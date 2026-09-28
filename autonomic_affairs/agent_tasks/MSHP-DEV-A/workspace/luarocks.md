# LuaRocks annexation investigation

Status: completed research output for `MSHP-DEV-A-080`.

Research date: 2026-09-28.

Upstream release checked: LuaRocks 3.13.0.

## Core conclusion

LuaRocks is not one global package database.

A safe Machine-Soul identity is conceptually:

```text
Lua runtime identity
+ rocks tree identity
+ rock package name/version
```

The LuaRocks tool installation itself is a separate subject from the rocks it manages.

## Current Windows installation

LuaRocks 3.13.0 remains the current upstream release at research time.

Upstream provides:

- a single-binary Windows package for machines that already have Lua;
- an all-in-one package containing Lua 5.1 and LuaRocks source/helper binaries;
- `INSTALL.BAT` with explicit Lua binding and tree/config options.

Current `install.bat` on main accepts Lua 5.1 through 5.5 even though parts of the prose Windows document still show an older 5.1–5.3 table. Treat executable installer behavior/source as newer than that stale table.

Sources:

- https://github.com/luarocks/luarocks/releases/tag/v3.13.0
- https://github.com/luarocks/luarocks/blob/main/docs/installation_instructions_for_windows.md
- https://github.com/luarocks/luarocks/blob/main/install.bat

Important Windows options include:

- `/LV <version>` — Lua version;
- `/LUA <dir>`, or explicit `/BIN`, `/LIB`, `/INC` — runtime location;
- `/TREE <dir>` — default system rock tree;
- `/CONFIG <dir>` — config location;
- `/SELFCONTAINED` — hardcoded self-contained layout;
- `/MW` or MSVC environment selection for native builds.

LuaRocks must match the interpreter's native runtime/ABI sufficiently to compile/link C modules correctly.

## Runtime binding

Normal CLI selection exposes:

```text
--lua-version <ver>
--lua-dir <prefix>
--tree <tree>
--local
--global
```

Passing explicit `--lua-version` or `--lua-dir` overrides hardcoded Lua paths in current configuration initialization.

A deterministic Machine-Soul invocation should therefore address the intended Lua runtime directly rather than rely on whichever `lua.exe` or generic LuaRocks configuration is ambient.

Relevant source:

- https://github.com/luarocks/luarocks/blob/main/src/luarocks/core/cfg.lua

## Rocks trees and scope

LuaRocks supports multiple local trees.

The config format documents `rocks_trees` as an ordered list of tree roots (or richer table entries with custom bin/lib/lua directories). Install target selection and runtime search precedence are tree-aware.

Common scopes are:

- project tree (for example created by `luarocks init`);
- user/local tree;
- system/global tree;
- arbitrary explicit `--tree <path>` tree.

On Windows, upstream's default installer is designed to allow both a system-wide tree and per-user rocks under the user's AppData area.

Source:

- https://github.com/luarocks/luarocks/blob/main/docs/config_file_format.md
- https://github.com/luarocks/luarocks/blob/main/docs/installation_instructions_for_windows.md

Machine-Soul must not collapse these to one “LuaRocks installed packages” list.

## Multiple Lua versions

Two Lua versions can coexist safely with distinct trees:

```text
Lua 5.4 runtime A
  -> tree A
  -> package inventory A

Lua 5.5 runtime B
  -> tree B
  -> package inventory B
```

The same LuaRocks installation can be invoked with explicit runtime/tree selectors for each environment.

A shared physical tree across Lua versions is possible only with deliberate versioned-directory configuration and is more subtle. For Machine-Soul's first implementation, **distinct explicitly identified trees per managed runtime/package environment are the safer baseline**.

This keeps:

- Lua modules;
- native C modules;
- executable wrappers;
- package metadata;
- uninstall effects

isolated by package environment.

## Configuration

LuaRocks configuration is executable Lua configuration data.

Important identity-affecting settings include:

- `rocks_trees`;
- Lua version and Lua directory/bindir/incdir/libdir;
- external dependency directories;
- compiler/build variables such as `CC`, `LD`, `MAKE`;
- server/repository selection;
- script wrapping behavior.

LuaRocks supports a normal config path, `LUAROCKS_CONFIG`, and version-specific environment variables such as `LUAROCKS_CONFIG_5_2`.

Machine-Soul does **not** need to assimilate the whole config merely to manage packages. Prefer explicit CLI/runtime/tree addressing and only manage configuration fields when they are truly selected desired state.

## Package inventory and deterministic operations

LuaRocks exposes the package lifecycle needed for ownership:

- `list` for installed packages;
- `list --porcelain` for script-oriented output;
- `show` for package details;
- `install` for package/version installation;
- `remove` for removal;
- `search`/server manifests for available packages;
- `make` for building a local rockspec/project;
- `pack` for producing rock archives.

Every inventory/mutation operation must be scoped with the intended runtime and tree when Machine-Soul owns a runtime-bound environment.

For safe ownership, record at least:

```text
runtime_instance_id
lua_version
tree_root
package_name
rock_version/revision
namespace if used
ownership
```

Architecture/compiler details may also be needed for native binary/native-source rocks.

## Exact ownership and dependency installs

Installing one requested rock may pull dependencies into the same tree.

Machine-Soul therefore needs to distinguish:

- **explicit desired roots** — packages the maintainer asked to own;
- **transitive installed dependencies** — packages present because desired roots require them.

Do not naively mark every package returned by `luarocks list` as independently desired.

Uninstall/reconciliation must let LuaRocks enforce dependency constraints rather than recursively deleting by filename.

## Native build dependencies

Many pure-Lua rocks need no compiler, but native rocks can require:

- a C compiler (MSVC or MinGW/GCC on Windows);
- Lua headers and import/static libraries matching the selected runtime;
- external libraries;
- architecture-compatible toolchains;
- build tools such as make/CMake depending on rockspec backend.

Upstream Windows docs explicitly warn that many packages need a C compiler and recommend an appropriately initialized Visual Studio command prompt when using MSVC.

This directly connects LuaRocks package state to the future native Windows toolchain investigation.

Machine-Soul should report missing toolchain/external dependencies as environment prerequisites rather than silently install arbitrary compilers as part of a rock mutation.

## Two-version scenario

Desired state:

```text
runtime lua-5.4-x64
tree C:\...\lua\5.4\rocks
desired roots: [luafilesystem, busted]

runtime lua-5.5-x64
tree C:\...\lua\5.5\rocks
desired roots: [luafilesystem]
```

Reconciliation should conceptually execute discovery/mutation with both runtime and tree explicit.

Installing/removing `busted` in the 5.4 tree must not affect the 5.5 tree.

A native `luafilesystem` build for 5.4 must use 5.4 headers/libs and the compatible architecture/toolchain; the 5.5 installation is a separate build/artifact identity.

## Project trees

Project-local `luarocks init` environments belong with project repositories unless the maintainer explicitly asks Machine-Soul to own them.

Global Machine-Soul annexation should not walk arbitrary source trees and absorb project-local Lua dependencies into machine-wide desired state.

## Initial Machine-Soul scope

A useful staged boundary is:

1. manage LuaRocks **tool installation** independently;
2. support explicitly selected runtime-bound trees as package environments;
3. manage only declared desired root-package inventories within those environments;
4. discover transitive packages but do not promote them to independent desired roots;
5. leave project-local trees and arbitrary ambient user/system trees unmanaged unless explicitly adopted.

This is stronger than “install LuaRocks only,” because package inventories are manageable safely when runtime+tree identity is explicit.

## Comparison hooks for pip/npm

Carry these questions into `MSHP-DEV-A-090/100/110`:

- Is package-environment identity runtime-specific?
- Are desired roots distinguishable from transitive packages?
- Can one package-manager installation address several runtime environments?
- How are user/global/project scopes represented?
- Are package inventories relocatable/exportable?
- What native toolchain/ABI coupling exists?
- Does runtime update/replacement destroy or invalidate package state?

## Conclusion

LuaRocks validates a first-class **runtime-bound package environment** concept.

It does not justify a generic implementation yet, but any eventual shared model must preserve exact environment identity and must never treat “LuaRocks packages on this machine” as one flat inventory.
