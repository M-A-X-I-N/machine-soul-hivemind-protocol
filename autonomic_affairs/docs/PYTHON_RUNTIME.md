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

`accumulated_instruments/__init__.py` and `annexation_procedures/__init__.py` establish the importable namespace. Importing the package must not mutate machine state.

## Dependency rule

Prefer the Python standard library.

External dependencies are allowed only when they provide enough concrete value to justify additional setup and portability cost. Do not introduce a dependency merely to save a few straightforward standard-library lines.

No dependency manager or lockfile is required until a real external dependency exists.

See [`OPERATION_ARCHITECTURE.md`](OPERATION_ARCHITECTURE.md) for the canonical dependency direction, dispatcher/engine responsibilities, strategy handler rules, custom-hook escape hatch, and duplication policy.

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

See [`ATOMIC_WRAPPERS.md`](ATOMIC_WRAPPERS.md) for the canonical per-application wrapper layout and `run(...)`/`main(...)` responsibilities.

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

The broad manager is now available at `annexation_procedures/manage_machine_soul.py`, but atomic wrappers remain usable independently and remain the semantic operation interfaces consumed by orchestration.

## Testing

CI smoke-tests the package and runs the Python contract suite on both Linux and Windows.

## Implemented shared core

V2-58 established the shared library APIs, and V2-60/V2-61 made the Python wrappers/core the canonical operation path:

- `model.context` — logical target account, operation context, conflict policy;
- `discovery` — repository-root marker discovery, platform/host/account resolution;
- `applications` — side-effect-free declaration loading/discovery;
- `configuration` — shared host/account source precedence and destination resolution;
- `filesystem` — portable file-symlink classification/creation;
- `state` — versioned JSON config/install state plus legacy Linux/Windows state readers;
- `operations.configuration` — safe Check/Apply/Unapply, backup/restore, rollback, relocation repair;
- `operations.installation` — Apt and WinGet handlers, managed/unmanaged provenance policy, dry-run;
- `operations.dispatcher` — generic capability/operation dispatch with no application-ID branches;
- `process` — shell-free subprocess execution;
- `primitives.invoke` — actual native-process invocation normalized through the versioned protocol.

The policy-heavy legacy Bash/PowerShell runtimes and platform-specific forwarding trees were retired after wrapper/core parity. Shell/PowerShell may return only for a future operation that genuinely earns a narrow native-primitive boundary.

### Windows symlink finding

The hosted Windows CI runner successfully creates and manages file symlinks through Python's `os.symlink`. Therefore the old PowerShell symlink implementation is **not** justified as a future native primitive merely for symlink creation.

Windows `os.readlink` may expose the target using the NT substitution-path spelling (for example an extended `\\?\` path) while normal filesystem paths use DOS/UNC spelling. Machine-Soul normalizes those equivalent spellings for identity comparison and keys deployment state by the logical declared destination rather than the alternate canonical representation.

This behavior is covered by the same configuration lifecycle tests on Windows and Linux.

### Legacy-state transition

The Python state layer reads both the new schema and existing legacy formats/hashes so previously recorded ownership/backup lineage is not intentionally stranded during migration. New Python writes use one JSON schema; destructive retirement of legacy readers waits until old state can no longer be required.


## Migration completion

V2-63 completed the transition from the parallel Bash/PowerShell policy runtime to the Python/declarative architecture.

The authoritative execution stack is now:

```text
atomic Python wrappers
    ↓
shared Python dispatcher/engines
    ↓
declarative application models + shared strategies
    ↓
portable Python helpers / justified external process boundaries
```

The repository keeps legacy state readers so backups/provenance created by the previous runtime are not stranded. That compatibility is intentional data migration support, not a second active runtime.
