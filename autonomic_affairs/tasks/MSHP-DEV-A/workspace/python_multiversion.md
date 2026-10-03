# Python multiversion annexation investigation

Status: completed research output for `MSHP-DEV-A-040`.

Research date: 2026-09-28.

## Current Windows direction changed materially

Python's official Windows story now centers on the **Python Install Manager**, not merely one traditional installer per runtime.

Current Python documentation/release pages describe the manager as the Windows tool for installing and managing runtimes. The traditional executable installer remains during Python 3.14/3.15 but is planned to stop with Python 3.16.

Current stable manager line at research time is 26.3 (released 2026-06-30); the stable CPython line shown by python.org is Python 3.14.7, with Python 3.15 in prerelease.

Sources:
- https://docs.python.org/3/using/windows.html
- https://www.python.org/downloads/windows/
- https://www.python.org/downloads/release/pymanager-260/

## Python Install Manager lifecycle

The official manager is itself installable through the Microsoft Store/MSIX, and Python documents programmatic WinGet installation using Store package ID `9NQ7512CXL7T`.

It provides:

- `py list` with machine-readable `json` / `jsonl` / path/prefix formats;
- `py list --only-managed` to distinguish runtimes owned by the manager;
- `py list --online` to inspect installable runtimes;
- `py install <TAG>...` to install one or more exact runtime tags;
- `py install --dry-run`;
- `py uninstall <TAG>...` for exact managed-runtime removal;
- `py uninstall --purge` for manager-owned runtime cleanup;
- `py -V:<TAG>` for deterministic runtime selection;
- `default_tag` / `PYTHON_MANAGER_DEFAULT` for selected/default runtime;
- platform/architecture suffixes and alternative distribution/company tags;
- user configuration at `%AppData%\Python\pymanager.json`.

Source: https://docs.python.org/3/using/windows.html

This is unusually close to Machine-Soul's desired multiversion contract already.

## Scope

The current Python Install Manager runtime lifecycle is **per-user only**. Python documentation explicitly states that manager/MSI runtimes are per-user and that the manager does not support ordinary per-machine runtime installation.

Machine-wide deployment can be approximated with `py install --target=<shared location>` plus administrator-managed PATH/registry/shortcut state, but such a target is not a normal manager-owned runtime.

Recommendation: initial Machine-Soul Python annexation should embrace the official manager's USER-scoped model rather than inventing system-wide Python semantics.

Source: https://docs.python.org/3/using/windows.html

## Multiversion and exact identity

Managed runtime identity is tag-based and richer than simply `major.minor`.

Tags can encode:

- exact/version-family CPython runtime;
- architecture/platform (for example arm64/32 variants);
- free-threaded builds (for example `3.14t`);
- embeddable distributions;
- other distributors/companies where exposed by the manager source.

`py list --one <TAG>` resolves using the same semantics used for execution, and machine-readable list output exposes executable/prefix identities.

This solves several problems Lua left open:

- desired installed version set;
- deterministic discovery;
- exact manager ownership;
- exact uninstall;
- selected/default runtime.

Machine-Soul should represent the desired set explicitly and translate it to manager tags rather than scanning PATH.

## Default/selected runtime

Python's manager already separates installed runtimes from selection.

The default runtime can be set through `default_tag` in `%AppData%\Python\pymanager.json` or `PYTHON_MANAGER_DEFAULT`. `python`/`py` then select the configured/default runtime, while `py -V:<TAG>` addresses an exact runtime.

This directly validates the Lua finding that **installed version set** and **selected/default runtime** are distinct desired state.

Recommendation: if Machine-Soul manages Python selection, prefer the manager's native `default_tag` configuration rather than introducing a parallel Machine-Soul shim.

## Global aliases and PATH

The manager creates versioned global aliases such as `python3.14.exe` in a configurable global commands directory (default `%LocalAppData%\Python\bin`) and uses Windows App Execution Aliases for the generic manager/default commands.

`py install --refresh` refreshes registrations/global aliases.

Python explicitly recommends `py` for scenarios involving multiple runtime versions. Scripted management should consider the unambiguous `pymanager` command because legacy Python Launcher installs may already occupy `py`.

Machine-Soul automation should therefore invoke `pymanager` where possible and treat legacy launcher collision as a discovery/migration condition, not silently assume `py` is the new manager.

## Legacy Python Launcher and unmanaged runtimes

Python recommends uninstalling the previous Python Launcher when adopting the Python Install Manager because both use `py`.

The manager can include unmanaged Python installations in discovery by default and can exclude them using `--only-managed`.

This fits Machine-Soul's ownership model well:

- manager-owned runtime instances can be exact owned candidates;
- unmanaged historical installers remain discoverable but unowned;
- takeover/adoption remains a separate future concern.

Removing the Install Manager itself does **not** remove the runtimes it managed. Reinstalling the manager can regain management of them. Conversely `--purge` cleans manager-owned runtimes.

## Manager configuration as assimilation

`%AppData%\Python\pymanager.json` is a documented user configuration surface. Relevant portable desired state may include:

- `default_tag`;
- `default_platform`;
- `automatic_install`;
- `include_unmanaged`;
- `confirm`;
- install source/index;
- list output defaults;
- install/global directories, when intentionally standardized.

Some paths are machine-specific and should not be blindly shared.

Because Machine-Soul may need to control `default_tag` and automatic-install behavior for deterministic annexation, Python Manager configuration is a plausible assimilation directive or native settings strategy.

## Update semantics

`py install --update` can update one or all managed runtimes. Python documentation warns that updating/replacing an install removes modifications to that runtime, including globally installed packages, while virtual environments continue to work.

That is important for later pip/package-management work:

> Globally mutating manager-owned Python runtime environments creates ownership coupling with runtime update/replacement.

Initial Machine-Soul runtime annexation should therefore avoid treating global pip packages as inseparable runtime state until `MSHP-DEV-A-090/110` decides package-environment semantics.

## Virtual environments

Virtual environments are not installed runtime versions.

The launcher/manager intentionally gives an active venv precedence when no explicit runtime version is requested. Project-local venv state belongs to the package/environment investigation, not the global runtime version set.

Machine-Soul runtime discovery must avoid counting each venv as another desired installed Python runtime.

## Third-party alternatives

### uv

`uv` can install and manage multiple Python versions on Windows, supports exact/version-range requests and alternative implementations such as PyPy, and uses Astral's `python-build-standalone` distributions.

Sources:
- https://docs.astral.sh/uv/concepts/python-versions/
- https://docs.astral.sh/uv/guides/install-python/

`uv` is a strong developer workflow/package/environment tool, but for **host-level CPython runtime annexation on Windows**, the official Python Install Manager has stronger native ownership/registry/launcher semantics and official provenance.

Keep uv relevant for project/package environment work rather than selecting it solely because it can also download Python.

### pyenv-win

`pyenv-win` remains a mature Windows-specific shim/version manager with install/list/global/local/uninstall semantics. It is useful historical/current evidence that multiversion Windows Python is tractable.

Source: https://github.com/pyenv-win/pyenv-win

However, the new official Python Install Manager now offers first-party Windows runtime management with machine-readable discovery and exact uninstall. Machine-Soul should prefer that official path unless a concrete pyenv-specific requirement appears.

### mise

`mise` can manage multiple Python versions and integrates with uv, but adds another manager layer and broader cross-tool semantics. It may become attractive if cross-runtime synthesis concludes one shared dev-tool manager is worth the tradeoff.

Source: https://mise.jdx.dev/lang/python.html

Do not choose mise for Python in isolation before comparing Node and Lua.

## Discovery model

For Python-manager-owned runtimes, Machine-Soul can use native manager discovery:

`pymanager list --only-managed --format=json` (or equivalent `py list`) plus exact runtime probes.

Preserve at least:

- manager tag;
- implementation/company;
- semantic version;
- architecture/platform/flavor;
- executable path;
- installation prefix;
- managed/unmanaged status;
- selected/default status.

Unmanaged installations should remain separate candidates using PEP 514 registry/native executable discovery as needed.

## Uninstall semantics

Exact manager-owned runtime removal maps directly to:

`pymanager uninstall --yes <TAG>`

Machine-Soul should still rediscover afterward and verify the exact candidate disappeared before deleting ownership provenance.

Removing the selected/default runtime should require explicit desired-state reconciliation. Depending on manager behavior, Machine-Soul should set a replacement default or refuse if desired default would become invalid.

## Conclusion

Unlike Lua, Windows Python now has a strong first-party multiversion manager that already exposes the exact lifecycle Machine-Soul wants.

Leading direction for synthesis:

> Install/manage the Python Install Manager as the annexation backend; express desired Python runtimes as an explicit set of manager tags; use native machine-readable list/install/uninstall; and express selected/default runtime through the manager's own configuration.

Do not implement this until Lua/Node comparison in `MSHP-DEV-A-070` confirms which concepts belong in shared runtime machinery and which should remain Python-manager-specific.
