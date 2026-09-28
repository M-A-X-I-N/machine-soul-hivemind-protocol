# Lua multiversion annexation findings

Durable findings from `MSHP-DEV-A-030` (2026-09-28):

- Include Lua 5.5 in current research; the original task's 5.1–5.4 list is now incomplete.
- Native Windows has no single clearly maintained manager that cleanly owns PUC Lua 5.1–5.5 plus LuaJIT with deterministic side-by-side install/select/discover/uninstall.
- LuaBinaries' version-qualified Windows executables make side-by-side instances naturally workable, though published binaries/package-manager manifests may lag newest upstream patches.
- Scoop can be a useful acquisition backend, but current Lua lines are split between Main/Versions apps and some manifests compete for generic `lua`/`luac` shims. Do not let package install order define the default runtime.
- Hererocks has a good isolated-prefix concept but materially stale published version coverage; luaenv is POSIX-oriented; current mise Lua vfox backend explicitly supports Linux/macOS, not native Windows.
- LuaJIT is a separate runtime flavor with rolling-release/source-build semantics, not simply 'Lua 5.1'.
- Desired installed version set and selected/default runtime are distinct state. Exact instance identity should include flavor, version, architecture, backend/source, prefix and executable.
- Uninstall one version must be exact and must handle selected/default ownership explicitly.
- Compare direct versioned prefixes versus Scoop-backed acquisition against Python/Node before creating generic runtime machinery.

Detailed research lives in `autonomic_affairs/agent_tasks/MSHP-DEV-A/workspace/lua_multiversion.md`.