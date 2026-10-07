# Developer annexation implementation map

This note is the agent-facing map for the first implemented developer-environment lifecycle. Human-facing capability details live in `meta/docs/RUNTIME_ANNEXATION_ARCHITECTURE.md`, `PACKAGE_ENVIRONMENT_ARCHITECTURE.md`, and `SUPPORT_MATRIX.md`.

## Implemented first-phase layers

- **Install-only developer applications:** Visual Studio Code and JetBrains Toolbox use exact USER-scoped WinGet application declarations. Configuration, profiles, extensions/plugins, Sync, IDE selection, and IDE version policy remain deliberately unowned.
- **Runtime core:** exact desired runtime sets, backend identity, selection/default state, provenance, explicit adoption, user/host backend scope, migration refusal, exact removal, and dependency guards.
- **Python:** official Python Install Manager backend, per-user multiversion lifecycle.
- **Node:** nvm-windows v2 backend, per-user multiversion lifecycle.
- **Lua/LuaJIT:** Machine-Soul-owned exact versioned prefixes and explicit launcher selection.
- **Package-environment core:** exact runtime/environment identity, explicit adoption/creation, managed-root ownership, unknown-root preservation, project/external refusal, secret-safe persisted state, and runtime-removal guards.
- **pip:** exact interpreter-bound environments.
- **npm:** exact Node runtime + global-prefix environments.
- **LuaRocks:** exact owned Lua/LuaJIT runtime + rocks-tree environments.

## Cross-layer invariants

1. Runtime selection/default changes are independent from package desired state.
2. An owned package environment blocks removal of its exact runtime.
3. Backend identity is provenance: matching versions under a different manager are not migration.
4. Project-local dependency state is outside global annexation unless explicitly reclassified/adopted by future designed policy.
5. Unknown top-level packages survive normal managed-root reconciliation.
6. Native package build prerequisites are reported; package backends do not silently annex compilers/SDKs.
7. Desired state and persisted diagnostics must not carry credentials.

## Validation map

The integrated acceptance test is:

`meta/tests/python/test_developer_environment_integration.py`

Backend-specific detail remains in:

- `test_python_runtime_backend.py`
- `test_node_runtime_backend.py`
- `test_lua_runtime_backend.py`
- `test_pip_package_backend.py`
- `test_npm_package_backend.py`
- `test_luarocks_package_backend.py`
- `test_runtime_core.py`
- `test_package_environment_core.py`

For implementation-phase completion, run the full repository validation matrix; do not substitute the integration test for ordinary application/configuration regression coverage.
