# pip annexation investigation

Status: completed research output for `MSHP-DEV-A-090`.

Research date: 2026-09-28.

Current stable pip documentation checked: 26.2.1.

## Core conclusion

pip is bound to a **specific Python environment**, not to “Python on the machine” in the abstract.

A safe Machine-Soul target is conceptually:

```text
Python runtime identity
+ Python environment identity
+ package desired-root inventory
```

The pip tool installation/version is a separate concern from the packages installed through it.

## Deterministic interpreter binding

For automation, invoke pip through the exact Python interpreter that owns the target environment:

```text
C:\exact\python.exe -m pip ...
```

Activation is only shell convenience. It must not be the ownership key.

pip also exposes a general `--python <python>` option for managing another interpreter/environment, but direct interpreter invocation remains the clearest exact binding when the target Python is already known.

Sources:

- https://pip.pypa.io/en/stable/user_guide/
- https://pip.pypa.io/en/stable/topics/python-option/

This fits the runtime synthesis directly: package-environment identity must reference an exact runtime/environment candidate, not whichever `python` or `pip` wins PATH.

## Environment kinds

### Base/runtime environment

Packages may be installed into an interpreter's default environment when that interpreter permits it.

This is **not automatically safe desired state**. The Python Install Manager research already established that updating/replacing manager-owned runtimes can remove modifications to those runtime environments, including globally installed packages.

Machine-Soul should therefore avoid making mutable packages inside a managed runtime prefix its default package-inventory strategy.

### User site

`pip install --user` targets the interpreter's user installation scheme. It is user-scoped, but still Python-version/interpreter-semantic state rather than one machine-global inventory.

The user site is convenient for human ad-hoc installs but awkward as a strong Machine-Soul ownership boundary because:

- multiple interpreter versions can expose different user-site locations;
- console scripts land in the user-base scripts directory;
- user-installed packages can interact with packages visible from the base interpreter;
- ownership is less isolated than a dedicated environment.

Treat user-site inventory as explicitly adoptable, not default Machine-Soul package state.

Source:

- https://packaging.python.org/en/latest/tutorials/installing-packages/

### Virtual environment

A virtual environment is an **environment identity**, not merely a package scope.

Its identity includes at least:

- environment root/path;
- base/interpreter relationship;
- exact environment Python executable;
- whether system-site-packages are visible;
- Machine-Soul ownership/adoption state.

Activation only changes shell command resolution. Machine-Soul can address a venv deterministically using its own interpreter executable without activation.

Python Packaging guidance describes virtual environments as isolated Python installations and recommends them for third-party packages.

Source:

- https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

Project-local `.venv` directories normally belong to their project repositories/workflows and should not be silently absorbed into machine-wide desired state.

### Externally managed environment

The PyPA Externally Managed Environments specification defines the `EXTERNALLY-MANAGED` marker. Outside a virtual environment, Python-specific installers such as pip should refuse normal mutation of such an interpreter's default environment and guide the user toward a virtual environment.

Source:

- https://packaging.python.org/en/latest/specifications/externally-managed-environments/

Machine-Soul should treat this as a hard ownership boundary in normal reconciliation.

Do **not** make `--break-system-packages` or equivalent override behavior a normal backend path. An explicit future adoption/override operation would need separate safety policy.

## Inventory and machine-readable discovery

Useful current interfaces include:

- `pip list --format=json` — installed distribution inventory;
- `pip inspect` — JSON environment/distribution metadata;
- `pip show` — package details;
- `pip check` — dependency consistency;
- `pip freeze` — requirements-format snapshot of installed packages.

Sources:

- https://pip.pypa.io/en/stable/cli/pip_list/
- https://pip.pypa.io/en/stable/cli/pip_inspect/
- https://pip.pypa.io/en/stable/reference/inspect-report/
- https://pip.pypa.io/en/stable/cli/pip_freeze/

`pip inspect` is especially useful for normalized discovery because its JSON report includes environment information and installed-distribution metadata.

## Why freeze is not desired state

`pip freeze` reports what is installed in requirements syntax. It is not a dependency solver result or a lockfile.

That means it cannot by itself answer:

- which packages were explicitly requested;
- which packages are transitive dependencies;
- why a package is present;
- whether a package should remain desired if another root is removed.

Therefore Machine-Soul must retain its own **declared desired roots** if it manages an environment.

`pip list --not-required` can be a useful diagnostic heuristic for packages that are not dependencies of other installed packages, but it is not provenance. A package can be intentionally desired while also serving as another package's dependency.

## Requirements files and locks

Requirements files are installation inputs, not automatically Machine-Soul machine-level desired-state files.

Project-owned requirements and lock files should remain project-owned by default.

The current Python packaging specifications also define `pylock.toml` for reproducible locked environments. That is valuable project dependency state, but it does not change the global ownership boundary.

Source:

- https://packaging.python.org/en/latest/specifications/pylock-toml/

Machine-Soul may later use a project's declared lock/input when explicitly asked to construct a project environment, but it should not ingest every requirements/lock file it sees.

## Install and uninstall

Within an explicitly owned environment, pip supports the needed package mutation lifecycle:

- `pip install <requirement>`;
- exact/version-constrained requirements;
- `pip uninstall <package>`;
- requirements-file-driven install/uninstall;
- direct URL/VCS/editable sources.

Source:

- https://pip.pypa.io/en/stable/cli/pip_install/
- https://pip.pypa.io/en/stable/cli/pip_uninstall/

Safe Machine-Soul provenance should preserve more than normalized name/version when source identity matters. Direct URL/editable installations can have meaningful origin metadata, which `pip inspect`/installed metadata can expose.

Do not delete package files manually; let pip own installation metadata and uninstall semantics.

## pip itself is separate state

pip may be:

- bundled/bootstrapped into a Python runtime;
- installed/upgraded inside a particular environment;
- absent from a runtime;
- managed differently by a distributor.

So “pip tool available for this environment” and “desired packages inside this environment” are separate state.

For a Machine-Soul-managed Python runtime, avoid gratuitously upgrading pip as a side effect of package reconciliation unless pip version policy is explicitly desired.

## Native builds and temporary build environments

When installing from source distributions, pip delegates builds to project build backends.

Current pip behavior normally creates an **isolated temporary build environment**, installs build-time Python dependencies there, then builds a wheel. Native extensions may compile C/C++ or other code.

Source:

- https://pip.pypa.io/en/stable/reference/build-system/

Machine-Soul package reconciliation therefore has several prerequisite dimensions that are not part of the final installed package inventory:

- compiler/toolchain availability;
- Python development headers/libraries appropriate to the runtime;
- external native libraries;
- architecture compatibility;
- temporary build-system dependencies.

Missing native prerequisites should be surfaced as prerequisites/errors, not silently trigger arbitrary compiler annexation.

`--no-build-isolation` changes ownership responsibility for build dependencies and should not be a default reconciliation mode.

## Indexes, authentication, and secrets

pip supports index credentials through URL authentication, `.netrc`, and keyring providers.

Source:

- https://pip.pypa.io/en/stable/topics/authentication/

Machine-Soul must not store passwords/API tokens in tracked desired-state files or task memory.

Portable non-secret index configuration can potentially be assimilated later, while credentials remain machine/user secret state or an external credential provider.

Be careful with machine automation and keyring: pip documents that some keyring providers may prompt, which can appear to hang under noninteractive wrapper tools.

## Multiple Python versions

Two simultaneously managed Python runtimes can each have independent package environments:

```text
Python 3.13 runtime
  -> environment A
  -> desired roots A

Python 3.14 runtime
  -> environment B
  -> desired roots B
```

Operations must invoke the exact environment/interpreter. Generic `pip.exe` or PATH order is not acceptable identity.

A venv created from one runtime is likewise its own environment identity; it must not silently migrate to another base runtime by relabeling provenance.

## System-site-packages visibility

A venv may be created with access to system site packages.

That means “packages importable in this environment” can be broader than “packages locally installed in this environment.”

Machine-Soul inventory must distinguish local owned distributions from inherited/visible distributions. pip's `--local` filtering is relevant when an environment has global visibility.

This is another reason environment-local installed state and effective import visibility must not be conflated.

## Recommended initial Machine-Soul boundary

For first-class pip package management:

1. support only **explicitly adopted package environments**;
2. bind each environment to an exact Python/runtime identity and environment root;
3. keep declared desired root packages separate from observed/transitive dependencies;
4. respect externally-managed base interpreters;
5. leave arbitrary project venvs unowned;
6. avoid treating user-site packages or mutable runtime-global packages as default desired state;
7. use machine-readable pip discovery and pip-native mutation;
8. keep credentials outside tracked configuration.

A future Machine-Soul-created dedicated environment for machine-level Python CLI tools may be useful, but that starts to overlap with pipx and should be investigated/taskified separately rather than invented inside this task.

## Comparison hooks for npm

Carry these questions into `MSHP-DEV-A-100/110`:

- Is package environment identity a runtime plus prefix/root?
- Does “global” actually mean runtime-manager-specific global state?
- Can desired roots be distinguished from transitives?
- Are project manifests/locks project-owned?
- Can global CLI tools be isolated from runtime package state?
- What happens to package state when the underlying runtime is removed or switched?
- Where can auth tokens appear?

## Conclusion

pip strongly validates the runtime-bound package-environment concept from LuaRocks, while adding a crucial ownership boundary:

> The exact Python environment is the mutation target, and some interpreter environments explicitly forbid pip ownership.

Machine-Soul should manage package inventories only in deliberately adopted environments, not flatten every interpreter/user/venv package into a machine-wide pip inventory.
