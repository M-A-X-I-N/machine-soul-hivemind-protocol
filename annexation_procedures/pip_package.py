"""Exact Python-environment pip package backend."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Callable, Mapping, Sequence

from .model import (
    DesiredPackageRoot,
    OperationContext,
    OperationResult,
    ObservedPackage,
    PackageEnvironment,
    PackageEnvironmentIdentity,
    PackageEnvironmentLocator,
    PackageEnvironmentOwnershipKind,
    PackageInventory,
    PackageMutationPolicy,
    PackageObservationKind,
    PackageRemovalTarget,
    PackageRootOwnership,
    PackageRootResolution,
    PackageRootStatus,
    PackageVerification,
    RuntimeInstance,
    RuntimeInstanceRef,
    redact_package_diagnostic,
)
from .process import ProcessResult, run_process


Runner = Callable[[list[str]], ProcessResult]

_NAME_NORMALIZER = re.compile(r"[-_.]+")
_REQUIREMENT_NAME = re.compile(
    r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"(?=\s*(?:$|\[|[<>=!~;@]))"
)
_PYTHON_ENVIRONMENT_PROBE = (
    "import json,site,sys,sysconfig;"
    "from pathlib import Path;"
    "stdlib=sysconfig.get_path('stdlib');"
    "print(json.dumps({"
    "'prefix':sys.prefix,"
    "'base_prefix':sys.base_prefix,"
    "'stdlib':stdlib,"
    "'python_version':'.'.join(map(str,sys.version_info[:3])),"
    "'is_venv':sys.prefix!=sys.base_prefix,"
    "'user_site':site.getusersitepackages(),"
    "'user_site_enabled':bool(site.ENABLE_USER_SITE),"
    "'externally_managed':bool(sys.prefix==sys.base_prefix and "
    "stdlib and (Path(stdlib)/'EXTERNALLY-MANAGED').is_file())"
    "}))"
)


class PipPackageEnvironmentError(RuntimeError):
    """An exact pip environment could not be addressed safely."""


@dataclass(frozen=True)
class PipEnvironmentTarget:
    """One explicitly enumerated Python environment that pip may inspect."""

    interpreter: Path
    runtime: RuntimeInstance
    runtime_scope_subject: str | None = None
    project_owned: bool = False
    ephemeral: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "interpreter", Path(self.interpreter))
        if self.runtime.subject != "python":
            raise ValueError("pip package targets must bind to a Python runtime.")
        if self.project_owned and self.ephemeral:
            raise ValueError("A pip target cannot be both project-owned and ephemeral.")


def normalize_python_distribution_name(name: str) -> str:
    """Normalize an installed/distribution name using the PyPA comparison rule."""

    value = _NAME_NORMALIZER.sub("-", name.strip()).casefold()
    if not value:
        raise ValueError("Python distribution name cannot be empty.")
    return value


def pip_desired_root(
    native_specifier: str,
    *,
    name: str | None = None,
) -> DesiredPackageRoot:
    """Build one pip-native desired root while preserving its exact specifier."""

    specifier = native_specifier.strip()
    if not specifier:
        raise ValueError("pip desired specifier cannot be empty.")

    inferred = name
    if inferred is None:
        match = _REQUIREMENT_NAME.match(specifier)
        if match is None:
            raise ValueError(
                "Cannot infer the pip project name from this specifier; pass name explicitly."
            )
        inferred = match.group(1)

    normalized = normalize_python_distribution_name(inferred)
    return DesiredPackageRoot(
        backend_key=normalized,
        native_specifier=specifier,
        normalized_name=normalized,
    )


class PipPackageEnvironmentBackend:
    """Current-account backend for exact interpreter/venv pip environments."""

    manager = "pip"
    name = "pip-exact-environment"

    def __init__(
        self,
        targets: Sequence[PipEnvironmentTarget],
        *,
        runner: Runner | None = None,
    ) -> None:
        if not targets:
            raise ValueError("At least one explicit pip environment target is required.")
        self._targets = tuple(targets)
        self._runner = runner
        self._recently_mutated: dict[tuple[str, str], str] = {}
        self._force_local_install: set[tuple[str, str]] = set()

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if not context.target_account.is_current:
            raise PipPackageEnvironmentError(
                "pip package reconciliation cannot safely mutate a non-current target account."
            )

    def _environment(self, context: OperationContext) -> Mapping[str, str]:
        environment = dict(os.environ)
        environment.update(context.environment)
        environment.pop("VIRTUAL_ENV", None)
        environment["PIP_NO_INPUT"] = "1"
        environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        return environment

    def _run(
        self,
        context: OperationContext,
        interpreter: Path,
        args: Sequence[str],
    ) -> ProcessResult:
        argv = [str(interpreter), *args]
        if self._runner is not None:
            return self._runner(argv)
        return run_process(argv, environ=self._environment(context))

    def _probe(
        self,
        context: OperationContext,
        target: PipEnvironmentTarget,
    ) -> dict[str, object]:
        result = self._run(context, target.interpreter, ["-c", _PYTHON_ENVIRONMENT_PROBE])
        if result.returncode != 0:
            raise PipPackageEnvironmentError(
                f"Python environment probe failed with exit code {result.returncode}."
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise PipPackageEnvironmentError(
                "Python environment probe returned malformed JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise PipPackageEnvironmentError(
                "Python environment probe returned an unexpected JSON shape."
            )
        required = ("prefix", "base_prefix", "python_version", "is_venv", "externally_managed")
        if any(key not in payload for key in required):
            raise PipPackageEnvironmentError(
                "Python environment probe omitted required identity fields."
            )
        return payload

    def _runtime_scope(
        self,
        context: OperationContext,
        target: PipEnvironmentTarget,
    ) -> str | None:
        if target.runtime_scope_subject is not None:
            return target.runtime_scope_subject
        if target.runtime.backend == "python-install-manager":
            return f"user:{context.target_account.name.casefold()}"
        return None

    def _backend_key(self, context: OperationContext, interpreter: Path) -> str:
        raw = os.path.normpath(str(interpreter))
        if context.platform.value == "windows":
            raw = raw.casefold()
        return f"interpreter:{raw}"

    def _target_for_environment(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PipEnvironmentTarget:
        matches = [
            target
            for target in self._targets
            if self._backend_key(context, target.interpreter)
            == environment.identity.backend_key
        ]
        if len(matches) != 1:
            raise PipPackageEnvironmentError(
                "pip environment identity no longer maps to exactly one configured target."
            )
        return matches[0]

    def discover_environments(
        self,
        context: OperationContext,
    ) -> tuple[PackageEnvironment, ...]:
        self._guard_context(context)
        environments: list[PackageEnvironment] = []
        seen: set[str] = set()

        for target in self._targets:
            probe = self._probe(context, target)
            backend_key = self._backend_key(context, target.interpreter)
            if backend_key in seen:
                raise PipPackageEnvironmentError(
                    "Duplicate pip targets resolve to the same exact interpreter."
                )
            seen.add(backend_key)

            prefix = str(probe["prefix"])
            base_prefix = str(probe["base_prefix"])
            is_venv = bool(probe["is_venv"])
            externally_managed = bool(probe["externally_managed"])

            if target.project_owned:
                observed_ownership = PackageEnvironmentOwnershipKind.PROJECT_OWNED
                classification = "project-venv" if is_venv else "project-python-environment"
            elif target.ephemeral:
                observed_ownership = PackageEnvironmentOwnershipKind.EPHEMERAL_UNMANAGED
                classification = "ephemeral-venv" if is_venv else "ephemeral-python-environment"
            elif externally_managed:
                observed_ownership = (
                    PackageEnvironmentOwnershipKind.EXTERNALLY_MANAGED_READ_ONLY
                )
                classification = "externally-managed-python"
            else:
                observed_ownership = PackageEnvironmentOwnershipKind.UNMANAGED
                classification = "venv" if is_venv else "runtime-global"

            runtime_ref = RuntimeInstanceRef.from_instance(
                target.runtime,
                scope_subject=self._runtime_scope(context, target),
            )
            identity = PackageEnvironmentIdentity(
                manager=self.manager,
                backend=self.name,
                backend_key=backend_key,
                locator=PackageEnvironmentLocator(
                    "python-interpreter",
                    {
                        "interpreter": str(target.interpreter),
                        "prefix": prefix,
                    },
                ),
                classification=classification,
                runtime=runtime_ref,
            )
            environments.append(
                PackageEnvironment(
                    identity,
                    ownership=observed_ownership,
                    mutation_policy=PackageMutationPolicy.READ_ONLY,
                    metadata={
                        "interpreter": str(target.interpreter),
                        "prefix": prefix,
                        "base_prefix": base_prefix,
                        "python_version": str(probe["python_version"]),
                        "is_venv": is_venv,
                        "externally_managed": externally_managed,
                        "user_site": str(probe.get("user_site") or ""),
                        "user_site_enabled": bool(probe.get("user_site_enabled", False)),
                    },
                )
            )

        return tuple(environments)

    def _pip(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        args: Sequence[str],
    ) -> ProcessResult:
        target = self._target_for_environment(context, environment)
        return self._run(context, target.interpreter, ["-m", "pip", *args])

    def check_tool(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> OperationResult:
        result = self._pip(context, environment, ["--version"])
        if result.returncode != 0:
            return OperationResult.failure(
                "pip_tool_unavailable",
                "pip is not available through the exact target interpreter.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "pip_tool_available",
            "pip is available through the exact target interpreter.",
            data={"version_output": result.stdout.strip()[:200]},
        )

    def _inspect_payload(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> dict[str, object]:
        result = self._pip(context, environment, ["inspect", "--local"])
        if result.returncode != 0:
            raise PipPackageEnvironmentError(
                f"pip inspect failed with exit code {result.returncode}."
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise PipPackageEnvironmentError("pip inspect returned malformed JSON.") from exc
        if not isinstance(payload, dict) or payload.get("version") != "1":
            raise PipPackageEnvironmentError(
                "pip inspect returned an unsupported report schema."
            )
        installed = payload.get("installed")
        if not isinstance(installed, list):
            raise PipPackageEnvironmentError(
                "pip inspect report is missing the installed array."
            )
        return payload

    def discover_inventory(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PackageInventory:
        payload = self._inspect_payload(context, environment)
        packages: list[ObservedPackage] = []
        seen: set[str] = set()

        for raw in payload["installed"]:
            if not isinstance(raw, dict):
                raise PipPackageEnvironmentError(
                    "pip inspect contains a non-object installed distribution."
                )
            metadata = raw.get("metadata")
            if not isinstance(metadata, dict):
                raise PipPackageEnvironmentError(
                    "pip inspect distribution is missing metadata."
                )
            name = metadata.get("name")
            version = metadata.get("version")
            if not isinstance(name, str) or not name.strip():
                raise PipPackageEnvironmentError(
                    "pip inspect distribution is missing its project name."
                )
            if version is not None and not isinstance(version, str):
                raise PipPackageEnvironmentError(
                    "pip inspect distribution has a non-string version."
                )

            normalized = normalize_python_distribution_name(name)
            backend_key = f"dist:{normalized}"
            if backend_key in seen:
                raise PipPackageEnvironmentError(
                    f"pip inspect reported duplicate distribution identity {normalized!r}."
                )
            seen.add(backend_key)

            diagnostic_metadata: dict[str, object] = {
                "installer": raw.get("installer"),
                "requested": raw.get("requested"),
                "metadata_location": raw.get("metadata_location"),
            }
            if "direct_url" in raw:
                diagnostic_metadata["direct_url"] = redact_package_diagnostic(
                    raw.get("direct_url")
                )
            safe_metadata = {
                key: value
                for key, value in diagnostic_metadata.items()
                if value is not None
            }
            packages.append(
                ObservedPackage(
                    backend_key=backend_key,
                    native_name=name,
                    version=version,
                    kind=(
                        PackageObservationKind.TOP_LEVEL
                        if raw.get("requested") is True
                        else PackageObservationKind.TRANSITIVE
                    ),
                    normalized_name=normalized,
                    metadata=safe_metadata,
                )
            )

        return PackageInventory(environment.identity.backend_key, tuple(packages))

    @staticmethod
    def _inventory_by_name(
        inventory: PackageInventory,
    ) -> dict[str, ObservedPackage]:
        return {
            package.normalized_name: package
            for package in inventory.packages
            if package.normalized_name is not None
        }

    def _specifier_satisfied(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> bool:
        result = self._pip(
            context,
            environment,
            [
                "install",
                "--dry-run",
                "--quiet",
                "--report",
                "-",
                "--no-input",
                "--disable-pip-version-check",
                root.native_specifier,
            ],
        )
        if result.returncode != 0:
            raise PipPackageEnvironmentError(
                f"pip dry-run verification failed with exit code {result.returncode}."
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise PipPackageEnvironmentError(
                "pip dry-run verification returned malformed JSON."
            ) from exc
        if not isinstance(payload, dict) or payload.get("version") != "1":
            raise PipPackageEnvironmentError(
                "pip dry-run verification returned an unsupported report schema."
            )
        install = payload.get("install")
        if not isinstance(install, list):
            raise PipPackageEnvironmentError(
                "pip dry-run verification is missing its install array."
            )
        return len(install) == 0

    def verify(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        desired_roots: Sequence[DesiredPackageRoot],
        inventory: PackageInventory,
        owned_roots: Sequence[PackageRootOwnership],
    ) -> PackageVerification:
        by_name = self._inventory_by_name(inventory)
        owned_by_key = {root.backend_key: root for root in owned_roots}
        resolutions: list[PackageRootResolution] = []

        for root in desired_roots:
            normalized = root.normalized_name or root.backend_key
            package = by_name.get(normalized)
            owned = owned_by_key.get(root.backend_key)
            recently_verified = (
                self._recently_mutated.get(
                    (environment.identity.backend_key, root.backend_key)
                )
                == root.native_specifier
            )

            satisfied = False
            if (
                package is not None
                and owned is not None
                and owned.native_specifier == root.native_specifier
                and owned.observed_key == package.backend_key
                and owned.removal_key == normalized
            ):
                satisfied = True
            elif package is not None and recently_verified:
                satisfied = True
            else:
                satisfied = self._specifier_satisfied(context, environment, root)
                if satisfied and package is None:
                    # pip may consider a venv requirement satisfied by an
                    # inherited system-site distribution even though
                    # pip inspect --local correctly omits it. Desired
                    # Machine-Soul roots must exist in the exact local
                    # environment, so force a local installation.
                    self._force_local_install.add(
                        (environment.identity.backend_key, root.backend_key)
                    )
                    satisfied = False

            if satisfied and package is not None:
                resolutions.append(
                    PackageRootResolution(
                        root.backend_key,
                        PackageRootStatus.SATISFIED,
                        observed_key=package.backend_key,
                        removal_key=normalized,
                    )
                )
            elif package is not None:
                resolutions.append(
                    PackageRootResolution(
                        root.backend_key,
                        PackageRootStatus.UPDATE_REQUIRED,
                        observed_key=package.backend_key,
                        removal_key=normalized,
                    )
                )
            else:
                resolutions.append(
                    PackageRootResolution(
                        root.backend_key,
                        PackageRootStatus.MISSING,
                    )
                )

        return PackageVerification(
            environment.identity.backend_key,
            tuple(resolutions),
        )

    @staticmethod
    def _looks_like_native_build_failure(output: str) -> bool:
        lowered = output.casefold()
        indicators = (
            "microsoft visual c++",
            "unable to find vcvarsall",
            "gcc: command not found",
            "clang: command not found",
            "failed building wheel",
            "could not build wheels",
        )
        return any(item in lowered for item in indicators)

    def _install_like(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
        *,
        operation: str,
    ) -> OperationResult:
        force_key = (environment.identity.backend_key, root.backend_key)
        args = [
            "install",
            "--no-input",
            "--disable-pip-version-check",
        ]
        if force_key in self._force_local_install:
            args.append("--ignore-installed")
        args.append(root.native_specifier)
        result = self._pip(context, environment, args)
        if result.returncode != 0:
            output = f"{result.stdout}\n{result.stderr}"
            if self._looks_like_native_build_failure(output):
                return OperationResult.failure(
                    "pip_native_build_prerequisite_missing",
                    "pip could not build the requested package; required native build prerequisites may be missing.",
                    data={"exit_code": result.returncode},
                )
            return OperationResult.failure(
                f"pip_package_{operation}_failed",
                f"pip {operation} failed for the exact target environment.",
                data={"exit_code": result.returncode},
            )

        self._recently_mutated[
            (environment.identity.backend_key, root.backend_key)
        ] = root.native_specifier
        self._force_local_install.discard(force_key)
        return OperationResult.success(
            f"pip_package_{operation}d",
            f"pip package {operation} completed for the exact target environment.",
            changed=True,
        )

    def install(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        return self._install_like(
            context,
            environment,
            root,
            operation="install",
        )

    def update(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        return self._install_like(
            context,
            environment,
            root,
            operation="update",
        )

    def remove(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        target: PackageRemovalTarget,
    ) -> OperationResult:
        name = target.normalized_name or target.native_name or target.removal_key
        result = self._pip(
            context,
            environment,
            [
                "uninstall",
                "--yes",
                "--disable-pip-version-check",
                name,
            ],
        )
        if result.returncode != 0:
            return OperationResult.failure(
                "pip_package_remove_failed",
                "pip uninstall failed for the exact target environment.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "pip_package_removed",
            "pip package removal completed for the exact target environment.",
            changed=True,
        )
