# Library-first operation architecture

This document fixes the dependency direction and extension rules for Machine-Soul's Python operation layer before implementation.

## Dependency direction

The architecture is intentionally one-way:

```text
interactive orchestrator
        |
        | imports/calls atomic wrapper run(...)
        v
per-application atomic wrappers
        |
        | application declaration + operation + context
        v
shared operation dispatcher / engines
        |
        +---- read immutable declaration/value models
        +---- use shared discovery/state/config/install helpers
        +---- interpret declared strategy types through reusable handlers
        +---- invoke native primitives only through the primitive boundary
        v
common semantic OperationResult
```

Rules:

- application declarations import model/value types only;
- declarations never import operation engines, wrappers, orchestration, or native scripts;
- wrappers import their declaration plus shared operation/presentation APIs;
- shared engines may import models, discovery, state, strategy handlers, and primitive invocation;
- the interactive orchestrator calls atomic wrapper interfaces rather than reimplementing or bypassing them;
- lower layers never import the orchestrator;
- platform-native primitives do not own Machine-Soul policy.

Avoid dependency cycles. When a lower layer appears to need knowledge from a higher layer, move the required abstraction downward rather than importing upward.

## Application declarations

`annexation_procedures/<application>/_application.py` is structured configuration written in Python.

It answers questions such as:

- what is this application?
- which platforms/capabilities are declared?
- which canonical config leaves exist?
- which destination strategies apply?
- which install/uninstall strategy is selected?

It does not decide runtime policy or perform work.

Declarations must remain safe to import during discovery, tests, and orchestration.

## Shared operation dispatcher

The shared library exposes one conceptual operation entry point:

```python
perform_operation(application, operation, context) -> OperationResult
```

The exact function/module name may change during implementation, but its responsibilities are fixed:

1. resolve/validate the requested platform and application capability;
2. select the generic engine for the requested `Operation`;
3. pass the application declaration and resolved operation context into that engine;
4. return one common semantic result.

The dispatcher may switch on the **operation enum** because operation identity is generic Machine-Soul behavior.

It must never switch on `application.id` to choose application-specific implementation.

Operation-specific engines own generic policy for concepts such as:

- apply/check/unapply configuration;
- install/check-installed/uninstall;
- source/destination resolution;
- state/provenance/backup rules;
- dry-run semantics;
- account targeting;
- capability/support handling.

## Operation context

All operation-wide runtime inputs travel through one resolved context object rather than being rediscovered independently by applications.

Conceptually it contains:

```text
OperationContext
    repository_root
    platform
    host identity
    target_account
    dry_run / conflict policy / other shared operation options
```

The concrete type lands with the shared core implementation.

Logical target account remains distinct from execution/elevation identity according to `ACCOUNT_TARGETING.md`.

Application wrappers and custom hooks receive the already-resolved context. They do not create alternative host/account detection systems.

## Strategy descriptors versus handlers

Declarative strategy **descriptors** are immutable data. Current examples live under `machine_soul.model.strategies`:

```text
AptPackage("fish")
WingetPackage("...")
RemoteInstallScript(...)
HomeRelativeDestination(...)
CustomInstaller(...)
```

Executable strategy **handlers** live in shared operation/library code.

Handlers dispatch by descriptor **type/capability**, not by application ID.

Conceptually:

```text
AptPackage              -> shared apt handler
WingetPackage           -> shared winget handler
RemoteInstallScript     -> shared remote-script handler
HomeRelativeDestination -> shared target-home resolver
CustomInstaller         -> explicitly supplied custom Python hook
```

The implementation may use an explicit registry, typed dispatch, or another simple Python mechanism. Do not create an opaque plugin framework merely to avoid a small clear mapping.

Adding a reusable descriptor type and its shared handler is the preferred extension mechanism when multiple applications can express the same behavior.

## Custom procedural escape hatch

When behavior cannot honestly be represented by an existing reusable strategy:

1. ask whether the behavior is actually a missing reusable Machine-Soul capability;
2. if reusable, add a generic descriptor/handler;
3. if genuinely unique, use ordinary Python through an explicit custom hook.

Custom application code:

- receives the standard operation inputs/context;
- returns the same common operation result as generic handlers;
- reuses shared helpers/primitives wherever practical;
- remains narrowly scoped to the genuine exception;
- does not create a parallel state/backup/account/reporting architecture.

A custom hook is preferable to a fake declarative mini-language containing arbitrary steps such as `If`, `Download`, `Copy`, or `Execute`.

The existence of a second similar custom hook is a strong signal that the shared library is missing a reusable strategy.

## Atomic wrappers

Atomic wrappers are the application-facing operation interface.

A wrapper identifies exactly:

- one application declaration;
- one operation;
- caller-provided/common operation options.

Everything else delegates to shared code.

The wrapper contract is defined in [`ATOMIC_WRAPPERS.md`](ATOMIC_WRAPPERS.md): wrappers are both importable and executable through one implementation path.

The orchestrator consumes those same wrapper interfaces so direct use and orchestration cannot drift into separate implementations.

## Interactive orchestration

The orchestrator may:

- discover declarations/wrappers;
- ask the maintainer which work to perform;
- invoke many atomic operations;
- choose targets/options;
- aggregate common results;
- present summaries.

It does not:

- resolve symlink policy itself;
- implement apt/winget/download behavior;
- know app-specific install details;
- write deployment state directly;
- call native primitives to bypass operation engines.

If orchestration needs new behavior, that behavior belongs in an atomic operation/shared engine first.

## Native primitive boundary

A native PowerShell/Bash helper exists only when a platform-native operation is materially clearer, safer, or unavailable cleanly from portable Python.

Python decides what action is requested and validates the returned structured result. Native code performs the narrow action.

The exact process protocol lands in V2-55.

## Presentation boundary

Operation engines produce semantic results, not human-formatted CLI output.

Presentation belongs above the engine:

- standalone wrapper `main()` renders a result and selects a process exit code;
- imported wrapper `run(...)` returns the result object;
- orchestrators aggregate result objects and render their own view;
- machine-readable presentation serializes the same semantics.

This prevents engine logic from depending on terminal/UI concerns.

## Duplication policy

Before adding behavior to an application-specific file, ask in this order:

1. Is it already generic shared behavior? Reuse it.
2. Is it a new behavior that multiple applications/platforms could reuse? Add a shared capability/strategy.
3. Is it truly unique? Add the smallest custom hook.

Never solve duplication with:

```python
if application.id == "some_app":
    ...
```

inside generic engines.

Application identity may appear in state keys, source paths, reporting data, and declaration lookup. It must not select hidden bespoke business logic inside shared operation code.

## Intended package ownership

As implementation lands, responsibility should converge approximately to:

```text
accumulated_instruments/machine_soul/
├── model/               immutable declarations and shared value objects
├── operations/          generic dispatcher + operation engines + strategy handlers
├── discovery/           environment/platform/account resolution
├── state/               state/provenance/backup persistence helpers
├── primitives/          structured native-process invocation/normalization
├── platforms/           justified platform-specific Python helpers
├── orchestration/       composition helpers for the broad manager
└── presentation/        human/machine rendering of common results
```

Do not create empty packages merely to satisfy this diagram. The implementation tasks create modules only when real behavior exists.

## Architectural test

A normal new application should usually require:

1. canonical config files;
2. one `_application.py` declaration selecting existing strategies;
3. uniform tiny operation wrappers.

If adding an ordinary application requires editing the core engine to mention the application by name, the architecture has failed this contract.
