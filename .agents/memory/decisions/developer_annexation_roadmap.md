# Developer annexation roadmap decision

Durable decision from `MSHP-DEV-A-120` (2026-09-28):

- The next executable developer-annexation phase is `MSHP-DEV-B`.
- Promote VS Code + JetBrains Toolbox installation together as one install-only task; do not invent editor configuration.
- Implement a shared runtime-instance core, then concrete Python Install Manager, nvm-windows v2, and Lua/LuaJIT versioned-prefix backends.
- Investigate MSVC/Visual Studio Build Tools/Windows SDK lifecycle before promising native-toolchain implementation; it is directly relevant to existing work and native package builds.
- Implement a shared package-environment core with exact runtime/environment identity and desired-root provenance, then prove it with combined pip/npm backends and a LuaRocks backend.
- Finish the phase with cross-layer runtime/package lifecycle integration and documentation.
- VS Code extensions + JetBrains plugins justify a future host-bound add-on inventory concept, but no task is promoted until desired add-ons/host ownership are selected.
- VS Code/JetBrains configuration remains blocked on maintainer-selected desired content and Sync/Backup ownership. Windows configuration candidates remain owned by `MSHP-WIN-CONFIG`.
- .NET/JDK/Rust/Go and lower-priority runtimes remain initiative gaps rather than zombie tasks.
- Install-only annexation remains a valid first-class capability independent from configuration management.

Detailed roadmap lives in `meta/tasks/archive/MSHP-DEV-A/workspace/developer_annexation_roadmap.md`.
