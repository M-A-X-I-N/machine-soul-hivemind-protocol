# Machine-Soul Hivemind Protocol

A cross-host configuration repository for keeping canonical tracked configuration files while safely linking them into the native locations expected by applications.

The active redesign lives on **experimental/v2**.

The first stable experimental v2 baseline is established on that branch. Promotion or merge to `main` requires separate authorization.

- experimental/v1 preserves the original repository.
- main is intentionally clean and is not the active v2 branch.
- experimental/v2 is the current implementation branch.
- `autonomic_affairs/agent_tasks.md` is the compact scheduling/Dispatch index for executable agent work; linked files contain full task specifications.

## Core model

Native application config paths are **file-level symbolic links** to canonical tracked files in this repository. Normal config application does not copy canonical config into a second drifting file.

MACHINE_SOUL identifies the absolute path of the active checkout. Repository-internal paths are derived from it.

Machine-local mutable state lives under the Git-ignored scratch/ tree, including backups, deployment state, local env/secrets, temporary files, logs, and caches where needed.

## Safety behavior

Apply follows: resolve → validate → classify destination → preserve existing unmanaged state → create file symlink → verify → record.

If a native config already exists, interactive Apply defaults to No. If replacement is accepted, the prior object is preserved under scratch/.

Unapply verifies that the current destination is still the object Machine-Soul expects before removing it. If a human or another tool replaced the managed link, Unapply reports a conflict instead of overwriting that new state. When safe, it restores the exact pre-Machine-Soul config that Apply displaced.

## Configuration resolution

Application configuration lives under assimilation_directives/<application>/.

Current final-file precedence is:

1. host + account
2. host common
3. default + account
4. default common

Shared fragments may exist, but deployment resolves to one concrete tracked file; the configuration-deployment runtime does not merge config content at deployment time.

Tracked configuration currently includes one Windows host variant and multiple Linux host variants. See autonomic_affairs/docs/CONFIGURATION_MODEL.md.

## Paired configuration and operation trees

Canonical application configuration lives under `assimilation_directives/<application>/...`.

The matching operational machinery lives under `annexation_procedures/<application>/...`.

Configured targets normally provide Apply config, Unapply config, and Check config from the annexation tree. Installation support may additionally provide Install and Uninstall there.

Installing an application is deliberately separate from applying its configuration. A pre-existing software installation is not silently claimed as Machine-Soul-owned merely because its executable exists.

See autonomic_affairs/docs/APPLICATION_CONTRACT.md and autonomic_affairs/docs/INSTALLATION_ARCHITECTURE.md.

## Oh My Posh and accounts

Linux host variants may carry independent tracked OMP configurations for normal and privileged target accounts. Each shell process initializes its own prompt environment; SSH and sudo do not transport a local shell's OMP state into the new process.

See autonomic_affairs/docs/SESSION_BOUNDARIES.md.

## Current support

See autonomic_affairs/docs/SUPPORT_MATRIX.md.

Windows Fish/Bash/Zsh are supported from an MSYS2/Cygwin-compatible POSIX shell through the `.sh` entry points under `annexation_procedures/`. Those adapters use cygpath for the shell environment's HOME/repository paths and delegate real symbolic-link creation to the Windows PowerShell runtime. Pure-PowerShell stubs remain NOT_IMPLEMENTED when no POSIX compatibility-shell context exists.

## Next-phase target architecture

The post-baseline roadmap is migrating toward a Python 3, library-first runtime with declarative per-application definitions, tiny atomic operation wrappers, an orchestration-only interactive manager, runtime environment discovery, and narrowly scoped platform-native primitives.

The current shell/PowerShell implementation remains authoritative for behavior that has not yet been migrated. See [autonomic_affairs/docs/next_phase_architecture.md](autonomic_affairs/docs/next_phase_architecture.md) for the target architecture and transition rules.

## Persistent project memory

- AGENTS.md defines stable agent rules.
- .agents/ is living agent memory.
- `autonomic_affairs/agent_tasks.md` owns executable-work scheduling, state, and Dispatch.

Agents are explicitly encouraged to preserve expensive-to-rediscover project knowledge under .agents/.