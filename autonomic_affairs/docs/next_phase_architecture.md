# Next-phase architecture

> **Status:** target architecture for the portability/taxonomy/Python phase beginning at V2-44.
>
> The current implementation still reflects the stable experimental v2 baseline in several places. This document describes the intended architecture to which V2-45 through V2-63 will migrate. Do not mistake a rule here for already-landed runtime behavior until its implementation task is complete.

## 1. Repository naming and meta structure

Repository-controlled multiword names use `lower_snake_case`.

The hyphen remains available for names that are externally defined or genuinely hyphenated rather than being the repository's word separator. Externally mandated names are preserved exactly when required, including tool-defined paths, executable names, package IDs, dotfiles, and application-owned filenames.

Examples of repository-owned target names include:

```text
assimilation_directives/
annexation_procedures/
accumulated_instruments/
configuration_deployment/
oh_my_posh/
```

Special/conventional root artifacts remain at the repository root when their location is useful or tool-defined, including dotfiles, `.github/`, `AGENTS.md`, and `README.md`.

Repository/project administration belongs under:

```text
autonomic_affairs/
```

Thematic repository-controlled top-level directories use names beginning with `a`. Tool-defined/conventional roots and externally mandated identifiers are exempt.

This namespace is for material about the repository itself rather than configuration or machine-management behavior. It will contain ordinary meta material such as documentation, tests, and the agent task ledger where practical.

The executable-work ledger is:

```text
autonomic_affairs/agent_tasks.md
```

"Agent tasks" means work that has been thought through enough to be theoretically executable. It is intentionally narrower than possible future concepts such as roadmap, objectives, or reminders. Those concepts may get separate artifacts later if they become useful.

## 2. Portability and environment discovery

The repository should require as little machine inventory as practical.

Facts that can be discovered reliably at execution time should be discovered rather than stored in tracked per-host inventory. This includes, where practical:

- hostname;
- operating system/platform;
- current account;
- home/config roots;
- privilege/elevation state;
- available package/runtime capabilities.

The current top-level tracked `hosts/*.env` inventory is therefore transitional and will be removed.

This does **not** mean host-specific configuration variants disappear. If concrete machines genuinely require different canonical configuration files, that host-specific distinction remains meaningful inside the configuration tree. What disappears is the requirement for a tracked registry merely to tell Machine-Soul facts the machine can discover for itself.

Explicit environment overrides may remain for tests or unusual environments, but ordinary execution must not depend on them.

Secrets and genuinely non-discoverable local values remain untracked machine-local state under `scratch/` or another documented ignored location.

## 3. Accounts are explicit targets, not inventory

Machine-Soul does not maintain an advisory list of accounts it supposedly manages.

Every operation has a **logical target account**. This is distinct from the process/execution identity.

The default target is the current account. Another account is selected explicitly through one common operation-context field and, for command-line entry points, one common option conceptually equivalent to:

```text
apply config
apply config --account root
check config --account root
unapply config --account root
```

The exact CLI parser is defined later, but these semantics are fixed:

- no explicit account means the current runtime account;
- an explicit account names the logical target whose config, destinations, state, and provenance are being inspected or mutated;
- discovering that an account exists does not make it managed;
- config files existing for an account do not make it managed;
- changing execution identity for elevation must **not** silently change the logical target account;
- target account metadata such as home/config roots is resolved centrally and supplied through operation context;
- account resolution may be platform-specific, but application wrappers must not implement their own lookup rules;
- unsupported/unresolvable cross-account targets fail explicitly rather than falling back to the current account;
- sudo/elevation is requested only for the narrow action that requires it;
- SSH, sudo, root, and normal-user process boundaries remain independent.

The shared Python model should expose a resolved target object conceptually containing at least:

```text
TargetAccount
    name
    is_current
    home
    platform identity fields when useful
```

and an operation context conceptually containing:

```text
OperationContext
    target_account
    conflict/output/dry-run options
    other operation-wide inputs
```

The exact class names are not sacred. The separation between logical target and execution identity is.

### Platform-resolution expectations

On POSIX/Linux, the standard account database is the preferred source for explicit-account metadata; Python's standard-library account facilities are sufficient for normal local users.

On Windows, current-account discovery is straightforward, but arbitrary other-account profile/home resolution and safe cross-account mutation must be treated as an explicit platform capability. If a reliable strategy is not yet implemented, a non-current target is reported unsupported rather than guessed.

Legacy `MACHINE_SOUL_ACCOUNT` overrides may remain temporarily for tests/migration. They are not the long-term user-facing account-selection interface.

## 4. Python is the shared runtime

Python 3 is the common language for new shared orchestration and policy.

Python 3 is an explicit prerequisite. Machine-Soul will not, in this phase, contain Bash/PowerShell bootstrap machinery whose job is to install Python before Machine-Soul can run. If Python is absent, it is installed manually before using the Python tooling.

Initially prefer the Python standard library. Add external dependencies only when their benefit clearly exceeds the portability/deployment cost.

Python owns portable decisions and policy whenever doing so remains clean.

Examples include:

- application/config resolution;
- environment discovery;
- state and provenance handling;
- backup/restore policy;
- conflict decisions;
- installation-strategy dispatch;
- target-account handling;
- process invocation;
- result normalization;
- CLI and interactive presentation.

## 5. Library-first implementation

The concrete dependency and extension rules are defined in [`OPERATION_ARCHITECTURE.md`](OPERATION_ARCHITECTURE.md).

Executable scripts are interfaces, not implementations.

Anything that can sensibly be genericized belongs in shared Python libraries/operation engines. Application entry points should not independently implement the same installation, configuration, state, account, package-manager, or reporting behavior.

The intended layers are:

```text
interactive orchestrator
        |
        | imports when possible; spawns only when required
        v
atomic operation wrappers
        |
        v
shared Python operation engines
        |
        +---- consume declarative application definitions
        |
        +---- invoke native platform primitives when genuinely necessary
```

Application-specific procedural code is allowed, but its existence should trigger a question first:

> Is this actually a reusable capability/strategy missing from the shared library?

If yes, add the reusable abstraction. If the behavior is genuinely unique, ordinary Python custom logic is preferable to stretching declarations into a miniature programming language.

## 6. Declarative applications

Each application is primarily described declaratively.

The conventional declaration file is:

```text
annexation_procedures/<application>/_application.py
```

After the snake_case migration, the surrounding paths follow that convention.

`_application.py` is deliberately visually different from executable operation wrappers:

- it describes the application;
- it is imported by wrappers/libraries/orchestration;
- executing it directly performs no operation and should have no side effects.

A declaration may describe:

- application identity/display metadata;
- supported operations;
- canonical configuration mappings;
- native configuration destinations;
- platform variants;
- installation/uninstallation strategy;
- installation verification;
- capabilities and unsupported/not-yet-implemented states;
- narrowly scoped hooks for genuine exceptions.

Prefer installation/configuration mechanisms in this order:

1. existing generic reusable strategy;
2. add a new generic reusable strategy when the behavior is broadly useful;
3. application-specific custom Python only when the behavior is genuinely unique.

Illustrative strategy concepts include:

```text
WingetPackage(...)
AptPackage(...)
RemoteInstallScript(...)
ReleaseArchive(...)
StandaloneBinary(...)
CustomInstaller(...)
```

The exact type names are not fixed by this document.

For example, an upstream Linux installer that must be downloaded and executed should normally select a reusable "remote install script" strategy. The declaration supplies the upstream URL/interpreter/verification details; the shared strategy owns temporary files, download/error handling, execution, cleanup, verification, and result normalization.

Do not create a declarative step language containing arbitrary `Download`, `If`, `Execute`, `Copy`, etc. Once behavior is genuinely procedural, use Python behind the same operation contract.

## 7. Atomic operation wrappers

Per-application wrapper files represent individual semantic actions.

Examples:

```text
annexation_procedures/fish/
├── _application.py
├── install.py
├── uninstall.py
├── check_installed.py
├── apply_config.py
├── unapply_config.py
└── check_config.py
```

A wrapper's job is exactly the operation its filename names.

For example, `fish/install.py` installs Fish according to the Fish declaration and reports the result. It does not:

- choose another application;
- scan unrelated applications;
- decide a multi-step machine workflow;
- implement Winget/apt itself;
- implement backup/state/account policy;
- contain an interactive menu.

Wrappers should be both executable and importable through one canonical implementation path. The expected shape is conceptually:

```python
def run(context=None):
    return shared_operation(application, context)

def main():
    result = run()
    present_result(result)
    return result.exit_code
```

The exact function signatures may be refined during implementation, but there must not be separate standalone and imported implementations.

The files present in an application's annexation directory should make its available atomic operations obvious to a human browsing the tree.

## 8. Interactive orchestration

The concrete orchestration contract is defined in [`INTERACTIVE_ORCHESTRATION.md`](INTERACTIVE_ORCHESTRATION.md).

The future broad/interactive Machine-Soul manager is intentionally the opposite of an operation implementation.

It may:

- enumerate applications/operations;
- invoke checks;
- ask the user what to do;
- compose workflows;
- apply the same operation to multiple applications;
- select target accounts/options;
- aggregate and format results;
- perform no mutation if the user chooses none.

It must not know how Fish is installed, how a symlink is created, how CMD AutoRun works, or how backup metadata is written.

When Python wrappers are available in-process, the orchestrator imports and calls their shared `run(...)` interface rather than spawning redundant Python processes merely for conceptual purity.

When a process boundary is actually required—native platform primitive, isolation boundary, external tool, or similar—the orchestrator/library may spawn it.

Imported and spawned paths normalize into the same result model before orchestration/presentation.

## 9. Common result model

Operations return a shared structured Python result rather than bespoke booleans or application-specific text parsing.

The precise class design will be finalized during implementation, but the semantic model includes at least:

- success/failure status;
- whether state changed;
- stable result/error code;
- human-readable detail;
- optional structured data.

Expected operational failures are valid operation results. They are distinct from an implementation/protocol malfunction.

The same semantic result must support:

- direct wrapper execution;
- imported wrapper calls;
- interactive orchestration;
- tests;
- machine-readable output;
- normalized results from native/spawned operations.

Presentation is separate from operation semantics. A standalone wrapper may render a concise human result while an automation mode emits structured data, but both originate from the same result object.

## 10. Native platform primitives

PowerShell/Bash/native scripts are retained only where they earn their existence.

They should be as small and dumb as practical.

Python decides **what** should happen. A native primitive performs the requested native action and reports structured facts.

Candidate primitive responsibilities include operations that are genuinely clearer/safer in the platform's native interface, such as some Windows registry/elevation behaviors or platform-specific filesystem/process details.

Do not create a native primitive merely because Windows and Linux implementations differ slightly. Prefer portable Python whenever the resulting code remains clean and trustworthy.

When Python crosses into a native process, use a defined machine-readable protocol. The initial direction is:

```text
stdout    versioned JSON result
stderr    low-level diagnostics/debugging
exit code process-level success/failure signal
```

Normal requested-operation failure with valid structured output is different from a primitive crashing or emitting invalid/missing protocol output.

Native result data is converted immediately into the same Python result model used everywhere else.

## 11. Safety laws remain unchanged

The runtime rewrite does not weaken the existing configuration safety contract.

Still required:

- tracked configuration files are canonical;
- managed config uses file-level symlinks;
- unmanaged existing state is never silently destroyed;
- accepted replacement preserves recoverable prior state;
- Apply validates/preserves/mutates/verifies/records in a safe order;
- Unapply verifies ownership before removal and restores displaced state when safe;
- unexpected external mutation becomes conflict, not blind overwrite;
- Check is read-only and reports meaningful state;
- installation ownership/provenance is distinct from configuration management;
- installing and applying configuration remain separate operations;
- `scratch/` remains the home for untracked machine-local mutable state.

The Python/declarative migration should centralize these guarantees rather than reimplement them independently per shell/application.

## 12. Migration discipline

Do not mechanically translate existing Bash/PowerShell line-for-line into Python.

Before porting a behavior, classify it as one of:

1. portable generic Python logic;
2. declarative application data;
3. reusable generic strategy/capability;
4. genuine application-specific hook;
5. genuine platform-native primitive;
6. obsolete behavior that should disappear.

Current implementation documents may continue to describe old runtime mechanics until the corresponding migration task lands. This document owns the target architecture during that transition.
