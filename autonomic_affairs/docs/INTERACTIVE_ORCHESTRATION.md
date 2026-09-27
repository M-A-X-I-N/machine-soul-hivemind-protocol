# Interactive orchestration contract

The broad Machine-Soul manager composes existing atomic application operations. It is an orchestration/presentation layer, not another place where application, installation, configuration, state, or platform policy may accumulate.

## Responsibility boundary

The orchestrator may:

- discover declared applications and their available atomic wrapper interfaces;
- inspect declared capability/support metadata for presentation and selection;
- ask the maintainer which applications/operations/targets/options to use;
- construct or reuse shared `OperationContext` values;
- invoke one or many atomic wrapper `run(...)` functions;
- sequence independent operations into a user-selected workflow;
- aggregate `OperationResult` values;
- present per-operation and aggregate summaries;
- stop, continue, or ask for confirmation based on explicit orchestration policy such as partial-change risk.

The orchestrator must not:

- implement config-source or destination resolution;
- manipulate symlinks/backups/deployment state directly;
- implement apt, WinGet, download, archive, or installer behavior;
- choose hidden application-specific strategies;
- reinterpret target-account semantics;
- call native primitives to bypass the shared operation engines;
- parse bespoke application output into meaning;
- duplicate an operation merely because it is being run as part of a multi-application workflow.

If the manager appears to need application/platform business logic, that behavior belongs in a declaration, reusable strategy, shared engine, atomic wrapper contract, or justified native primitive first.

## Invocation path

In-process Python orchestration prefers importing and calling atomic wrapper `run(...)` functions:

```text
interactive manager
    ↓
application wrapper run(context)
    ↓
shared perform_operation(...)
    ↓
OperationResult
```

The manager does not bypass the wrapper and import application-specific implementation internals directly.

This keeps direct wrapper use, orchestrated use, and tests on the same semantic execution path.

## When spawning is justified

Do not spawn a Python wrapper merely to preserve an artificial process boundary.

A process boundary is justified when it provides a real property, for example:

- invoking a non-Python/native primitive through the shared primitive layer;
- explicit isolation required by an operation;
- invoking an external tool whose process is itself the operation boundary;
- a future remote execution boundary deliberately introduced by architecture.

Spawned/native results are normalized into the common `OperationResult` model before orchestration consumes them.

The orchestrator must never contain operation-specific parsing rules for spawned output.

## Discovery

Application discovery should be generic.

Conceptually, the manager may enumerate application directories/declarations under `annexation_procedures/` and determine:

- application ID/display name;
- declared platforms;
- supported/not-implemented/unsupported capabilities;
- available wrapper modules.

Discovery must remain side-effect free. Importing `_application.py` or wrapper modules during discovery cannot perform operations.

The implementation task may choose a simple explicit registry or filesystem/module discovery. Do not create a plugin framework unless real needs justify it.

## Operation selection

An orchestration workflow is a collection of ordinary atomic operations.

Examples:

- check configuration for all discovered applications;
- install one selected application;
- apply configuration to several selected applications;
- check installation state and then offer applicable actions.

The manager decides **which** atomic operations to request, not **how** they work.

Capability declarations remain authoritative. The manager may hide, disable, or explain unsupported/not-implemented actions in its UI, but it does not manufacture alternate implementations.

## Context propagation

Shared operation-wide inputs are resolved once where practical and propagated explicitly:

- repository root;
- platform;
- discovered host/environment facts;
- logical target account;
- dry-run;
- conflict policy;
- structured/common options.

Per-operation context may differ when the maintainer deliberately selects different targets/options, but applications do not rediscover those semantics independently.

Changing process/elevation identity does not silently change the logical target account.

## Aggregation

Every atomic operation returns an `OperationResult`.

The orchestrator may build an aggregate view containing, for each attempted operation:

- application;
- operation;
- target;
- result status/code/message;
- changed flag;
- useful structured data.

Aggregation does not replace or mutate the original semantic results.

A workflow with mixed outcomes must preserve them individually. Do not collapse:

```text
SUCCESS + FAILURE + ERROR
```

into a vague single boolean.

Especially preserve `changed=true` on non-success results because it may indicate partial mutation requiring attention.

## Workflow continuation

The implementation may offer configurable/interactive continuation behavior, but the baseline safety rule is:

- trustworthy expected semantic failures may be shown and the maintainer may choose whether independent operations continue;
- protocol/programming failures are not silently downgraded to ordinary semantic failures;
- partial-change or rollback-risk outcomes must be surfaced prominently before dependent mutation continues.

Do not invent automatic rollback across unrelated applications merely because operations were selected together. Each atomic engine owns the transaction/safety guarantees of its own operation unless a future explicit cross-operation transaction model is designed.

## Presentation

Presentation belongs above semantic operation execution.

The interactive manager may provide richer views than standalone wrappers, including:

- tables;
- grouped application status;
- selectable actions;
- aggregate summaries;
- structured machine output where useful.

It consumes `OperationResult` objects directly and never scrapes the standalone human renderer.

The broad manager is allowed to do nothing: discovery/status presentation without a selected mutating action is a valid workflow.

## Importability and testing

Orchestration behavior should itself be library-first.

UI/input handling should be separable from composition logic so tests can supply predetermined selections/contexts without terminal automation.

Useful contract tests should be able to provide fake wrapper callables returning controlled `OperationResult` objects and verify:

- selected wrappers are called exactly once with intended context;
- unrelated wrappers are not invoked;
- result ordering/identity is retained;
- mixed statuses remain distinguishable;
- partial-change results are not lost;
- no operation policy is implemented by the orchestration layer.

## Architectural test

The orchestrator should theoretically be able to operate on a newly added ordinary application without modifying orchestrator business logic.

If adding an application requires teaching the broad manager how that application's config/install behavior works, the abstraction boundary has failed.


## Implemented manager surface

The broad manager entry point is:

```text
python accumulated_instruments/manage_machine_soul.py
```

With no workflow argument it presents an interactive menu. The initial workflows are deliberately small and generic:

- check configuration for every discovered application;
- apply configuration to an explicit selected application set;
- check installation state and apply configuration only to positively detected installed applications;
- exit without performing any operation.

For automation/testing the same entry point accepts `--workflow list`, `--workflow check-config-all`, `--workflow apply-config`, and `--workflow apply-installed`.

Composition lives in `accumulated_instruments.machine_soul.orchestration`. Wrapper discovery loads the platform-neutral atomic wrapper modules and validates their `APPLICATION`, `OPERATION`, and `run(context)` interface. Workflow execution calls those `run(...)` functions directly.

A non-success result with `changed=true` stops later mutation in the same baseline workflow so partial-change risk cannot be silently buried. Mixed ordinary semantic outcomes remain present as individual attempts in the workflow report.
