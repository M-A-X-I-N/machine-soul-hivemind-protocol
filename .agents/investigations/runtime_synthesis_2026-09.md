# Runtime/version-management synthesis findings

Durable findings from `MSHP-DEV-A-070` (2026-09-28):

- Lua, Python, and Node justify a shared **runtime instance** model with intentionally desired simultaneous versions.
- Desired runtime versions are a set; multiple owned desired versions must not be treated like accidental duplicate package candidates.
- Selected/default runtime is independent desired state and must not be inferred from install order or PATH precedence.
- Exact instance identity includes backend ownership plus ecosystem-relevant version/flavor/distribution/architecture/prefix keys.
- Runtime lifecycle should delegate to backend-specific strategies. Python's official manager, Node managers, Lua direct/acquisition-backed approaches, and future rustup-style ecosystems should not be forced through one universal manager.
- Backend identity is durable provenance. Switching managers is an explicit migration/adoption problem, not a normal update.
- Generic package-manager provenance should continue to own manager/tool installation; runtime-instance provenance should represent versions owned through that backend.
- Removing a selected runtime requires atomic reselection to another desired instance or safe refusal.
- Project-local runtime selection files normally remain project-owned, not global Machine-Soul desired state.
- No implementation tasks were created at this checkpoint because `MSHP-DEV-A-080..110` must first establish how runtime-bound package environments affect the architecture. `MSHP-DEV-A-120` should taskify implementation using both syntheses.

Detailed synthesis lives in `autonomic_affairs/agent_tasks/MSHP-DEV-A/workspace/runtime_synthesis.md`.
