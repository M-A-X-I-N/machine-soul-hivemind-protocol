# LuaRocks annexation findings

Durable findings from `MSHP-DEV-A-080` (2026-09-28):

- LuaRocks tool installation and LuaRocks-managed package inventories are separate ownership subjects.
- A safe package-environment identity includes the exact Lua runtime/version plus an exact rocks-tree root; package name/version alone is insufficient.
- Current LuaRocks CLI can explicitly select `--lua-version`, `--lua-dir`, and `--tree`; use these instead of ambient PATH/config when Machine-Soul owns an environment.
- LuaRocks supports project, user/local, system/global, and arbitrary explicit trees. Do not flatten them into one inventory.
- Multiple Lua versions should initially use distinct explicitly identified trees. Shared cross-version trees are possible but add versioned-layout complexity without useful first-implementation value.
- Track declared desired root rocks separately from transitively installed dependencies.
- Native rocks couple package state to Lua ABI/headers/libs, architecture, compiler, and external dependencies; missing native toolchains should be reported as prerequisites rather than silently annexed.
- Project-local LuaRocks trees normally remain project-owned.
- Initial useful Machine-Soul scope can include explicitly selected runtime-bound package inventories, not merely LuaRocks installation, provided runtime+tree identity is exact.

Detailed research lives in `autonomic_affairs/tasks/archive/MSHP-DEV-A/workspace/luarocks.md`.
