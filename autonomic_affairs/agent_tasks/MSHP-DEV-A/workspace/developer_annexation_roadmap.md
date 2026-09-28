# Developer annexation implementation roadmap

Status: completed roadmap synthesis for `MSHP-DEV-A-120`.

Synthesis date: 2026-09-28.

## Decision

The next implementation phase is `MSHP-DEV-B`.

It deliberately separates:

- immediately promotable install-only editor subjects;
- a shared runtime-instance core from runtime-specific backends;
- a shared package-environment core from package-manager-specific backends;
- native Windows toolchain research where evidence is strong but the lifecycle contract still needs deeper validation;
- configuration/add-on work that cannot proceed without maintainer-selected desired state.

No task exists merely because an ecosystem is common.

## Planned execution graph

```text
DEV-A-120
├─ DEV-B-010  VS Code + Toolbox install-only promotion
├─ DEV-B-020  Windows native toolchain investigation
└─ DEV-B-030  runtime annexation core
   ├─ DEV-B-040  Python backend
   ├─ DEV-B-050  Node backend
   ├─ DEV-B-060  Lua/LuaJIT backend  <-- also consumes B-020
   └─ DEV-B-070  package-environment core
      ├─ DEV-B-080  pip + npm backends  <-- also consumes B-040/B-050
      └─ DEV-B-090  LuaRocks backend    <-- also consumes B-060

DEV-B-100 integrates B-010 + runtime/package backends end to end.
```

## Why these task boundaries

### DEV-B-010 — editor installation

VS Code and JetBrains Toolbox are both already proven scoped-WinGet subjects and require no invented configuration. Combining them avoids two tiny declaration-only tasks while keeping settings/plugins/profiles explicitly out of scope.

### DEV-B-020 — native Windows toolchain research

MSVC/Build Tools/Windows SDK state is directly relevant to existing maintainer work and to native pip/npm/LuaRocks/LuaJIT builds, but current evidence is not yet enough to commit to a safe component/workload mutation model. A dedicated investigation is therefore executable now; speculative implementation is not.

### DEV-B-030 — runtime core

Lua, Python, Node, and likely future Rust/.NET/JDK/Go all justify exact runtime instances, desired installed sets, separate selected/default state, backend identity, and exact lifecycle provenance. This is the reusable core.

### DEV-B-040/050/060 — concrete runtime backends

Three backends are needed to prove the core against genuinely different ecosystems:

- Python: strong first-party manager;
- Node: strong third-party Windows manager;
- Lua/LuaJIT: Machine-Soul-owned versioned-prefix model where no universal manager is adequate.

This avoids an abstraction tested only against one easy ecosystem.

### DEV-B-070 — package-environment core

LuaRocks, pip, and npm all justify exact environment identity and desired-root inventories, but none justify one command vocabulary. This core therefore owns identity/provenance/policy, not package-manager syntax.

### DEV-B-080 — pip + npm together

Implementing pip and npm in one task intentionally stresses the shared model across two very different semantics: interpreter/venv/read-only environments versus Node/global-prefix environments. Splitting them would reduce the value of the abstraction checkpoint and create extra bookkeeping.

### DEV-B-090 — LuaRocks separately

LuaRocks depends on the harder Lua runtime backend and explicit rocks-tree binding, so it remains a separate task rather than inflating B-080.

### DEV-B-100 — lifecycle integration

Cross-layer safety such as “do not delete a runtime while owned package environments still depend on it” is important enough to validate after all concrete backends exist rather than assuming unit-level correctness composes automatically.

## Editor/IDE add-on inventory decision

VS Code extensions and JetBrains plugins provide enough evidence for a reusable **host-bound add-on inventory** concept:

```text
host application/instance/profile
+ native add-on identifier/specifier
+ declared desired roots
+ backend-native list/install/uninstall
```

However, no implementation task is promoted now.

Reasons:

- no maintainer-selected extension/plugin inventory exists;
- VS Code profile/Settings Sync ownership is not selected;
- JetBrains desired IDE product/version set is not selected;
- Toolbox CLI lifecycle remains too immature to make IDE-instance management a stable prerequisite.

This concept remains a structured DEV-ENV gap and can be promoted when desired content/ownership is selected.

Do not reuse runtime package-environment types blindly for editor add-ons; the conceptual inventory pattern is similar, but host/profile semantics differ.

## Configuration ownership decision

The following remain **initiative gaps, not executable tasks**:

### VS Code

Potential Machine-Soul-owned categories:

- base user `settings.json`;
- `keybindings.json`;
- user snippets;
- exported/imported profiles;
- extensions.

Before promotion, the maintainer must choose desired content and category ownership relative to VS Code Settings Sync.

### JetBrains / Toolbox

Potential categories:

- Toolbox `.settings.json`;
- IDE product/version lifecycle;
- IDE settings export/import;
- plugins;
- Rider-specific settings layers.

Before promotion, the maintainer must choose desired content/products/plugins and cloud Backup-and-Sync ownership. IDE lifecycle automation also needs a stable backend.

### Windows config candidates

WinGet user settings, WSL `.wslconfig`, OpenSSH client config, PowerToys DSC, and Sandbox profiles remain owned by `MSHP-WIN-CONFIG`. DEV does not duplicate them.

## Installation-only remains first-class

A developer tool does not need assimilatable configuration to be useful.

This is explicit in B-010 and in runtime backends: Machine-Soul may safely own installation/version lifecycle while leaving configuration/project state entirely external.

## Deferred runtime/tool ecosystems

Keep as initiative-only until concrete demand:

- .NET SDK/runtime;
- Java/JDK;
- Rust/rustup;
- Go;
- Ruby;
- PHP;
- Perl.

The shared runtime model must not block them, but they do not earn executable tasks merely to exercise extensibility.

## Backend choices carried forward

### Python

Initial Windows backend: official Python Install Manager.

### Node

Initial Windows backend: nvm-windows v2 Community.

The shared backend contract preserves future fnm/Volta/mise alternatives and makes migration explicit rather than automatic.

### Lua / LuaJIT

Initial model: Machine-Soul-owned exact versioned prefixes with selected/default routing separate from acquisition.

- PUC Lua can use trusted versioned binaries when exact requested artifacts exist, otherwise a validated source-build path.
- LuaJIT remains a separate runtime flavor and may require native source builds.
- B-020 informs safe native toolchain prerequisites.

## Package inventory policy carried forward

For an explicitly managed environment:

- Machine-Soul owns declared desired roots;
- transitive packages are observed dependency state;
- unknown/unowned roots are preserved by default;
- externally-managed/read-only environments cannot be mutated;
- project-local environments remain project-owned by default;
- credentials stay outside tracked state;
- runtime removal must first reconcile bound owned environments.

## Traceability

| DEV-B task | Primary evidence |
|---|---|
| B-010 | DEV-A-010, DEV-A-020 |
| B-020 | DEV-A-060 plus native-build findings from A-080/A-090/A-100/A-110 |
| B-030 | DEV-A-030/A-040/A-050/A-070 |
| B-040 | DEV-A-040/A-070 |
| B-050 | DEV-A-050/A-070 |
| B-060 | DEV-A-030/A-060/A-070 + B-020 |
| B-070 | DEV-A-080/A-090/A-100/A-110 |
| B-080 | DEV-A-040/A-050/A-090/A-100/A-110 + B-040/B-050/B-070 |
| B-090 | DEV-A-030/A-080/A-110 + B-060/B-070 |
| B-100 | all implemented DEV-B capabilities |

## Dispatch after DEV-A-120

When this synthesis task is complete, the first independently eligible tasks are:

1. `MSHP-DEV-B-010`;
2. `MSHP-DEV-B-020`;
3. `MSHP-DEV-B-030`.

They are ordered for useful early wins and context flow, not because later-listed eligible tasks are semantically blocked by earlier dispatch entries.

## Deliberately absent tasks

No current tasks for:

- VS Code settings/profiles/extensions;
- JetBrains IDE versions/settings/plugins;
- .NET/JDK/Rust/Go/Ruby/PHP/Perl;
- pipx/uv/Poetry/Yarn/pnpm/Corepack;
- project dependency environments;
- runtime-manager migration;
- full exclusive package-environment convergence.

These remain future promotion points only when evidence/desired state warrants them.
