# Atomic application wrapper contract

Atomic wrappers are the stable direct/importable interface for performing one semantic operation on one declared application.

## Final application operation layout

The target layout is platform-neutral at the wrapper level:

```text
annexation/
└── <application>/
    ├── _application.py
    ├── apply_config.py
    ├── unapply_config.py
    ├── check_config.py
    ├── install.py
    ├── uninstall.py
    └── check_installed.py
```

Only operations that are part of the application's declared surface need wrapper files.

Do **not** create separate `windows/` and `linux/` Python wrappers for the same semantic operation. Platform support, strategies, and capability state belong in the application declaration and shared engines.

File presence is not the support contract. `PlatformDeclaration.capabilities` remains authoritative for `SUPPORTED`, `UNSUPPORTED`, and `NOT_IMPLEMENTED`.

## `_application.py`

`_application.py` is not a wrapper.

It exposes the side-effect-free application declaration:

```python
APPLICATION = Application(...)
```

Executing/importing it performs no operation.

The leading underscore intentionally distinguishes the declaration from directly executable operation files.

## Canonical wrapper shape

Every ordinary operation wrapper follows one conceptual pattern:

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from annexation.applications import load_application
from annexation.model import Operation
from annexation.operations import perform_operation
from annexation.presentation import wrapper_main

APPLICATION = load_application(Path(__file__).with_name("_application.py"))
OPERATION = Operation.INSTALL


def run(context=None):
    return perform_operation(APPLICATION, OPERATION, context)


def main(argv=None):
    return wrapper_main(run, argv)


if __name__ == "__main__":
    raise SystemExit(main())
```

`load_application(Path(__file__).with_name("_application.py"))` is deliberate: it works identically when the wrapper is executed directly by path or imported under another module name, without depending on an ambient `_application` top-level import. The responsibilities and single implementation path are fixed.

## `run(...)`

`run(...)` is the canonical semantic operation interface.

It:

- accepts a resolved/shared `OperationContext` or permits the shared library to resolve the default context when omitted;
- binds one application declaration to one `Operation`;
- calls the shared operation dispatcher;
- returns one common `OperationResult`.

It does not:

- parse command-line arguments;
- print user-facing output;
- translate results into process exit codes;
- discover unrelated applications;
- choose a multi-operation workflow;
- implement package/config/state/account/platform behavior.

The orchestrator calls this same `run(...)` path.

## `main(...)`

`main(argv=None)` is only the process/CLI adapter.

It delegates common concerns to shared helpers:

1. parse common operation CLI options;
2. resolve an `OperationContext`;
3. call `run(context)`;
4. render the common result;
5. map the result to the shared process exit contract.

Result and exit semantics are defined in [`OPERATION_RESULTS.md`](OPERATION_RESULTS.md).

The wrapper itself must not reimplement common argument parsing.

Common option concepts include target account, dry-run, conflict policy, and machine-readable presentation where relevant. Their concrete parser/API belongs in shared runtime code.

If an application appears to need bespoke wrapper flags, first determine whether the option is actually a reusable operation capability. Genuine application-specific procedural inputs belong behind an explicit custom operation/strategy contract rather than ad-hoc parsing duplicated across wrappers.

## Import safety

Importing any wrapper must be non-mutating.

All work begins only when `run(...)` or `main(...)` is explicitly invoked.

Module-level code may:

- establish repository-root importability;
- import declarations/shared APIs;
- define constants/functions.

It may not:

- inspect/mutate deployment state;
- execute native tools;
- install software;
- prompt;
- create files/directories;
- perform environment-dependent operation selection with side effects.

## Direct execution from any working directory

A wrapper must be runnable by path without requiring an editable package install or preconfigured `PYTHONPATH`.

For wrappers directly under `annexation/<application>/`, the standardized repository bootstrap is:

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
```

Do not invent different bootstrap logic per application.

## Operation naming

Wrapper filenames match the `Operation` vocabulary:

| File | Operation |
|---|---|
| `apply_config.py` | `APPLY_CONFIG` |
| `unapply_config.py` | `UNAPPLY_CONFIG` |
| `check_config.py` | `CHECK_CONFIG` |
| `install.py` | `INSTALL` |
| `uninstall.py` | `UNINSTALL` |
| `check_installed.py` | `CHECK_INSTALLED` |

Do not invent synonymous per-application names.

## Capability behavior

A wrapper may exist even when some platforms report `UNSUPPORTED` or `NOT_IMPLEMENTED`.

The shared dispatcher reads the current platform declaration and produces the appropriate common result. The wrapper does not contain platform branches to implement divergent business logic.

## Error and result boundary

Expected operational states/failures return the common result model.

Wrappers should not catch broad exceptions merely to turn programming/protocol failures into fake successful result objects. The semantic-failure versus exceptional-malfunction distinction is defined in [`OPERATION_RESULTS.md`](OPERATION_RESULTS.md).

## Orchestrator relationship

The interactive orchestrator imports/calls wrapper `run(...)` functions when operating in-process.

It does not bypass wrappers and call application-specific internals directly.

This ensures direct CLI use, interactive orchestration, and tests all exercise the same semantic operation path.

## Uniformity test

For an ordinary application, adding a wrapper should require changing only:

- which `APPLICATION` declaration is imported;
- which `Operation` constant is bound.

If the wrapper needs package-manager logic, filesystem policy, target-account lookup, platform branching, state persistence, or custom output parsing, that behavior belongs somewhere lower/shared.
