# Machine-Soul Hivemind Protocol

A cross-host machine-assimilation repository for reproducing desired machine state: canonical configuration where useful, plus installation and other operational machinery where configuration management is irrelevant or unnecessary.

The active development/experimental iteration lives on **main**.

The former `experimental/v2` line produced the current Python/declarative architecture and is being promoted into `main` as the ordinary working branch. A future large redesign may split the then-current iteration back onto versioned branches if there is an actual reason to do so.

- `experimental/v1` preserves the original repository iteration.
- `main` is the current implementation/development branch.
- `autonomic_affairs/agent_tasks.md` is the compact scheduling/Dispatch index for executable agent work; `autonomic_affairs/agent_tasks/` contains active specifications, temporary workspaces, and structured archived task history.

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

## Assimilation directives and annexation procedures

`assimilation_directives/` contains the canonical tracked **instructions for how an assimilated machine should behave**: application configuration and other desired behavioral content that belongs in version control.

`annexation_procedures/` contains the executable **machinery used to take over / bring a machine into the collective**: shared Python runtime, application declarations, install/uninstall/discovery/configuration operations, wrappers, and broad orchestration.

The names describe different responsibilities, not two halves that every target must possess.

A target may legitimately have:

- annexation procedures with assimilation directives — for example an application whose installation and configuration are both managed;
- annexation procedures without assimilation directives — for example a runtime/tool whose useful Machine-Soul responsibility is installation/version lifecycle only;
- assimilation directives whose application is already installed independently — configuration management does not imply installation ownership.

There is no requirement that an annexation target have configuration files merely to be considered supported.

`accumulated_instruments/` is reserved for tracked tools/programs/scripts that are useful enough to keep with the repository but are not intrinsically part of the assimilation/annexation system.

Installing an application is deliberately separate from applying its configuration. A pre-existing software installation is not silently claimed as Machine-Soul-owned merely because its executable exists.

See autonomic_affairs/docs/APPLICATION_CONTRACT.md and autonomic_affairs/docs/INSTALLATION_ARCHITECTURE.md.

## Oh My Posh and accounts

Linux host variants may carry independent tracked OMP configurations for normal and privileged target accounts. Each shell process initializes its own prompt environment; SSH and sudo do not transport a local shell's OMP state into the new process.

See autonomic_affairs/docs/SESSION_BOUNDARIES.md.

## Current support

See autonomic_affairs/docs/SUPPORT_MATRIX.md.

All application operations use platform-neutral Python wrappers directly under `annexation_procedures/<application>/`. Windows Fish/Bash/Zsh configuration remains dependent on an MSYS2/Cygwin-compatible environment because their declared destination strategy intentionally uses that environment's `HOME` and `cygpath`; the operation policy itself is Python.

## Next-phase target architecture

The post-baseline roadmap is migrating toward a Python 3, library-first runtime with declarative per-application definitions, tiny atomic operation wrappers, an orchestration-only interactive manager, runtime environment discovery, and narrowly scoped platform-native primitives.

The Python operation core and atomic wrappers are now authoritative for migrated operation behavior. See [autonomic_affairs/docs/next_phase_architecture.md](autonomic_affairs/docs/next_phase_architecture.md) for the target architecture and transition rules.

## Broad manager

Atomic wrappers remain independently usable, while the broad manager composes them without duplicating application logic:

```text
python annexation_procedures/manage_machine_soul.py
```

Run it without a workflow for the interactive menu, or use its workflow options for scripted status/application selection. See `autonomic_affairs/docs/INTERACTIVE_ORCHESTRATION.md`.

## Persistent project memory

- AGENTS.md defines stable agent rules.
- .agents/ is living agent memory.
- `autonomic_affairs/agent_tasks.md` owns executable-work scheduling, state, and Dispatch.

Agents are explicitly encouraged to preserve expensive-to-rediscover project knowledge under .agents/.