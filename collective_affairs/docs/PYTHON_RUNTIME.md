# Python runtime architecture

## Baseline

Machine-Soul's shared runtime is Python 3.

The current minimum baseline is **Python 3.10**. This keeps compatibility broad enough for existing Linux installations while allowing modern standard-library/type syntax. Raising the minimum requires an explicit portability reason.

Python is a prerequisite. This phase does not install Python, bootstrap Python, create a mandatory virtual environment, or require package installation before repository scripts can run.

## Repository-local package

Shared Python behavior lives under:

```text
accumulated_instruments/
└── machine_soul/
```

The repository root is the import root. The package is not required to be installed into `site-packages`.

`accumulated_instruments/__init__.py` and `accumulated_instruments/machine_soul/__init__.py` establish the importable namespace. Importing the package must not mutate machine state.

## Dependency rule

Prefer the Python standard library.

External dependencies are allowed only when they provide enough concrete value to justify additional setup and portability cost. Do not introduce a dependency merely to save a few straightforward standard-library lines.

No dependency manager or lockfile is required until a real external dependency exists.

## Intended module boundaries

The exact files may evolve as V2-51 through V2-58 land, but responsibilities are divided conceptually as:

```text
machine_soul/
├── model/          shared declarations, context, result/value objects
├── operations/     generic install/config/check/unapply engines
├── strategies/     reusable declared strategies such as package installers
├── discovery/      host/platform/account/environment resolution
├── primitives/     native-process protocol and invocation
├── platforms/      justified platform-specific Python helpers
├── orchestration/  multi-operation composition used by the broad manager
└── presentation/   human/machine result rendering
```

Do not create empty directories merely to match this diagram. Add modules when their task supplies real behavior.

## Direct wrapper execution

Application wrappers must remain directly executable by path without requiring `pip install -e .` or setting `PYTHONPATH` first.

A direct wrapper therefore uses one standardized bootstrap before importing Machine-Soul:

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
```

For a wrapper at `annexation_procedures/<application>/<operation>.py`, `parents[2]` is the repository root.

This tiny bootstrap is infrastructure required to make a repository-local package importable; it is not application business logic. Do not let wrapper-specific behavior accumulate there.

When the same wrapper is imported by the orchestrator, the repository root is already established by the top-level entry point and the same `run(...)` implementation is called.

## Entry-point rule

Executable Python files are interfaces.

They may:

- establish repository-local importability;
- parse their operation's common command arguments;
- load the application declaration;
- call one shared engine;
- present the returned common result;
- convert that result to a process exit code.

They do not contain installation/configuration/state/platform policy.

## Invocation expectations

During this phase, valid usage may look like:

```text
python3 annexation_procedures/fish/install.py
python annexation_procedures/fish/install.py
```

depending on platform/interpreter command.

A future broad interactive entry point may provide a more convenient interface, but atomic wrappers remain usable independently.

## Testing

CI smoke-tests that the repository-local package imports and accepts the configured Python baseline on both Linux and Windows. Later tasks add behavioral/unit tests as real Python functionality appears.
