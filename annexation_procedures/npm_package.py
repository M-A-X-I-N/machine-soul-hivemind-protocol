"""Exact runtime/global-prefix npm package backend."""

from __future__ import annotations

from dataclasses import dataclass
import json
import ntpath
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
    Platform,
    RuntimeInstance,
    RuntimeInstanceRef,
    redact_package_diagnostic,
)
from .process import ProcessResult, run_process


Runner = Callable[[list[str]], ProcessResult]
_NPM_NAME = re.compile(r"^(?:@[^/@\s]+/[^/@\s]+|[^/@\s][^@\s]*)$")


class NpmPackageEnvironmentError(RuntimeError):
    """An exact npm global-prefix environment could not be addressed safely."""


@dataclass(frozen=True)
class NpmGlobalTarget:
    """One exact Node runtime whose npm global prefix may be inspected."""

    runtime: RuntimeInstance
    npm_cli: Path | None = None
    runtime_scope_subject: str | None = None

    def __post_init__(self) -> None:
        if self.runtime.subject != "node":
            raise ValueError("npm package targets must bind to a Node runtime.")
        if self.runtime.executable is None or self.runtime.prefix is None:
            raise ValueError("npm package targets require exact Node executable and prefix.")
        if self.npm_cli is not None:
            object.__setattr__(self, "npm_cli", Path(self.npm_cli))


def normalize_npm_package_name(name: str) -> str:
    """Normalize an npm package name for exact inventory comparison."""

    value = name.strip().casefold()
    if not value or _NPM_NAME.fullmatch(value) is None:
        raise ValueError(f"Invalid npm package name: {name!r}.")
    return value


def _infer_npm_package_name(specifier: str) -> str:
    value = specifier.strip()
    if value.startswith("@"):
        slash = value.find("/")
        if slash <= 1:
            raise ValueError(
                "Cannot infer scoped npm package name; pass name explicitly."
            )
        version_at = value.find("@", slash + 1)
        candidate = value if version_at < 0 else value[:version_at]
    else:
        version_at = value.find("@", 1)
        candidate = value if version_at < 0 else value[:version_at]

    return normalize_npm_package_name(candidate)


def npm_desired_root(
    native_specifier: str,
    *,
    name: str | None = None,
) -> DesiredPackageRoot:
    """Build one npm-native global desired root."""

    specifier = native_specifier.strip()
    if not specifier:
        raise ValueError("npm desired specifier cannot be empty.")
    normalized = (
        normalize_npm_package_name(name)
        if name is not None
        else _infer_npm_package_name(specifier)
    )
    return DesiredPackageRoot(
        backend_key=normalized,
        native_specifier=specifier,
        normalized_name=normalized,
    )


class NpmGlobalPackageEnvironmentBackend:
    """Current-user npm global-prefix backend bound to exact Node runtimes."""

    manager = "npm"
    name = "npm-runtime-global-prefix"

    def __init__(
        self,
        targets: Sequence[NpmGlobalTarget],
        *,
        runner: Runner | None = None,
    ) -> None:
        if not targets:
            raise ValueError("At least one explicit npm global target is required.")
        self._targets = tuple(targets)
        self._runner = runner
        self._recently_mutated: dict[tuple[str, str], str] = {}

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if context.platform is not Platform.WINDOWS:
            raise NpmPackageEnvironmentError(
                "The initial npm backend is bound to Windows Node runtime semantics."
            )
        if not context.target_account.is_current:
            raise NpmPackageEnvironmentError(
                "npm package reconciliation cannot safely mutate a non-current target account."
            )

    def _runtime_scope(
        self,
        context: OperationContext,
        target: NpmGlobalTarget,
    ) -> str | None:
        if target.runtime_scope_subject is not None:
            return target.runtime_scope_subject
        if target.runtime.backend == "nvm-windows-v2":
            return f"user:{context.target_account.name.casefold()}"
        return None

    @staticmethod
    def _default_npm_cli(target: NpmGlobalTarget) -> Path:
        assert target.runtime.prefix is not None
        return (
            target.runtime.prefix
            / "node_modules"
            / "npm"
            / "bin"
            / "npm-cli.js"
        )

    def _npm_cli(self, target: NpmGlobalTarget) -> Path:
        return target.npm_cli or self._default_npm_cli(target)

    def _environment(self, context: OperationContext) -> Mapping[str, str]:
        environment = dict(os.environ)
        environment.update(context.environment)
        environment["NPM_CONFIG_UPDATE_NOTIFIER"] = "false"
        environment["NPM_CONFIG_FUND"] = "false"
        environment["NPM_CONFIG_AUDIT"] = "false"
        return environment

    def _run(
        self,
        context: OperationContext,
        target: NpmGlobalTarget,
        args: Sequence[str],
    ) -> ProcessResult:
        assert target.runtime.executable is not None
        argv = [
            str(target.runtime.executable),
            str(self._npm_cli(target)),
            *args,
        ]
        if self._runner is not None:
            return self._runner(argv)
        return run_process(argv, environ=self._environment(context))

    @staticmethod
    def _normalized_windows_path(value: str) -> str:
        return ntpath.normcase(ntpath.normpath(value))

    def _identity_key(
        self,
        target: NpmGlobalTarget,
        prefix: str,
    ) -> str:
        return (
            f"{target.runtime.backend}:{target.runtime.backend_key}"
            f"|prefix:{self._normalized_windows_path(prefix)}"
        )

    def _prefix_and_root(
        self,
        context: OperationContext,
        target: NpmGlobalTarget,
    ) -> tuple[str, str]:
        prefix_result = self._run(context, target, ["prefix", "--global"])
        if prefix_result.returncode != 0 or not prefix_result.stdout.strip():
            raise NpmPackageEnvironmentError(
                f"npm global prefix discovery failed with exit code {prefix_result.returncode}."
            )
        root_result = self._run(context, target, ["root", "--global"])
        if root_result.returncode != 0 or not root_result.stdout.strip():
            raise NpmPackageEnvironmentError(
                f"npm global root discovery failed with exit code {root_result.returncode}."
            )
        return prefix_result.stdout.strip(), root_result.stdout.strip()

    def _target_for_environment(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> NpmGlobalTarget:
        matches: list[NpmGlobalTarget] = []
        for target in self._targets:
            prefix, _ = self._prefix_and_root(context, target)
            if self._identity_key(target, prefix) == environment.identity.backend_key:
                matches.append(target)
        if len(matches) != 1:
            raise NpmPackageEnvironmentError(
                "npm environment identity no longer maps to exactly one configured runtime/prefix."
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
            prefix, root = self._prefix_and_root(context, target)
            backend_key = self._identity_key(target, prefix)
            if backend_key in seen:
                raise NpmPackageEnvironmentError(
                    "Duplicate npm targets resolve to the same runtime/global-prefix identity."
                )
            seen.add(backend_key)

            assert target.runtime.executable is not None
            runtime_ref = RuntimeInstanceRef.from_instance(
                target.runtime,
                scope_subject=self._runtime_scope(context, target),
            )
            identity = PackageEnvironmentIdentity(
                manager=self.manager,
                backend=self.name,
                backend_key=backend_key,
                locator=PackageEnvironmentLocator(
                    "npm-global-prefix",
                    {
                        "node": str(target.runtime.executable),
                        "npm_cli": str(self._npm_cli(target)),
                        "prefix": prefix,
                        "root": root,
                    },
                ),
                classification="runtime-global-prefix",
                runtime=runtime_ref,
            )
            environments.append(
                PackageEnvironment(
                    identity,
                    ownership=PackageEnvironmentOwnershipKind.UNMANAGED,
                    mutation_policy=PackageMutationPolicy.READ_ONLY,
                    metadata={
                        "node_version": target.runtime.version,
                        "runtime_backend": target.runtime.backend,
                        "runtime_backend_key": target.runtime.backend_key,
                        "prefix": prefix,
                        "root": root,
                    },
                )
            )

        return tuple(environments)

    def check_tool(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> OperationResult:
        target = self._target_for_environment(context, environment)
        result = self._run(context, target, ["--version"])
        if result.returncode != 0:
            return OperationResult.failure(
                "npm_tool_unavailable",
                "npm is not available through the exact target Node runtime.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "npm_tool_available",
            "npm is available through the exact target Node runtime.",
            data={"version": result.stdout.strip()[:100]},
        )

    def _inventory_payload(
        self,
        context: OperationContext,
        target: NpmGlobalTarget,
    ) -> dict[str, object]:
        result = self._run(
            context,
            target,
            ["ls", "--global", "--all", "--json"],
        )
        if result.returncode != 0:
            raise NpmPackageEnvironmentError(
                f"npm global inventory reported package-tree problems (exit code {result.returncode})."
            )
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise NpmPackageEnvironmentError(
                "npm global inventory returned malformed JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise NpmPackageEnvironmentError(
                "npm global inventory returned an unexpected JSON shape."
            )
        dependencies = payload.get("dependencies", {})
        if not isinstance(dependencies, dict):
            raise NpmPackageEnvironmentError(
                "npm global inventory dependencies must be an object."
            )
        return payload

    @staticmethod
    def _safe_node_metadata(node: Mapping[str, object]) -> dict[str, object]:
        metadata: dict[str, object] = {}
        for key in ("extraneous", "missing", "invalid", "overridden", "link"):
            if key in node:
                metadata[key] = redact_package_diagnostic(node[key])
        if "resolved" in node:
            metadata["resolved"] = redact_package_diagnostic(node["resolved"])
        return metadata

    def discover_inventory(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PackageInventory:
        target = self._target_for_environment(context, environment)
        payload = self._inventory_payload(context, target)
        packages: list[ObservedPackage] = []
        seen: set[str] = set()

        def visit(
            name: str,
            raw: object,
            *,
            path: tuple[str, ...],
            top_level: bool,
        ) -> None:
            if not isinstance(raw, dict):
                raise NpmPackageEnvironmentError(
                    "npm inventory contains a non-object dependency node."
                )
            normalized = normalize_npm_package_name(name)
            version = raw.get("version")
            if version is not None and not isinstance(version, str):
                raise NpmPackageEnvironmentError(
                    "npm inventory dependency has a non-string version."
                )
            backend_key = (
                f"pkg:{normalized}"
                if top_level
                else "transitive:" + ">".join(path)
            )
            if backend_key in seen:
                raise NpmPackageEnvironmentError(
                    f"npm inventory contains duplicate logical identity {backend_key!r}."
                )
            seen.add(backend_key)
            packages.append(
                ObservedPackage(
                    backend_key=backend_key,
                    native_name=name,
                    version=version,
                    kind=(
                        PackageObservationKind.TOP_LEVEL
                        if top_level
                        else PackageObservationKind.TRANSITIVE
                    ),
                    normalized_name=normalized,
                    metadata=self._safe_node_metadata(raw),
                )
            )

            nested = raw.get("dependencies", {})
            if nested is None:
                return
            if not isinstance(nested, dict):
                raise NpmPackageEnvironmentError(
                    "npm inventory dependency children must be an object."
                )
            for child_name, child in nested.items():
                visit(
                    str(child_name),
                    child,
                    path=(*path, normalize_npm_package_name(str(child_name))),
                    top_level=False,
                )

        for package_name, raw in payload.get("dependencies", {}).items():
            normalized = normalize_npm_package_name(str(package_name))
            visit(
                str(package_name),
                raw,
                path=(normalized,),
                top_level=True,
            )

        return PackageInventory(environment.identity.backend_key, tuple(packages))

    @staticmethod
    def _top_level_by_name(
        inventory: PackageInventory,
    ) -> dict[str, ObservedPackage]:
        return {
            package.normalized_name: package
            for package in inventory.packages
            if package.kind is PackageObservationKind.TOP_LEVEL
            and package.normalized_name is not None
        }

    def _specifier_satisfied(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> bool:
        target = self._target_for_environment(context, environment)
        result = self._run(
            context,
            target,
            [
                "ls",
                "--global",
                "--depth=0",
                "--json",
                root.native_specifier,
            ],
        )
        if result.returncode != 0:
            return False
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise NpmPackageEnvironmentError(
                "npm desired-root verification returned malformed JSON."
            ) from exc
        if not isinstance(payload, dict):
            raise NpmPackageEnvironmentError(
                "npm desired-root verification returned an unexpected JSON shape."
            )
        dependencies = payload.get("dependencies", {})
        if not isinstance(dependencies, dict):
            return False
        desired_name = root.normalized_name or root.backend_key
        return any(
            normalize_npm_package_name(str(name)) == desired_name
            for name in dependencies
        )

    def verify(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        desired_roots: Sequence[DesiredPackageRoot],
        inventory: PackageInventory,
        owned_roots: Sequence[PackageRootOwnership],
    ) -> PackageVerification:
        by_name = self._top_level_by_name(inventory)
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
                satisfied = self._specifier_satisfied(
                    context,
                    environment,
                    root,
                )

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
            "node-gyp",
            "gyp err! find vs",
            "could not find any visual studio installation",
            "msbuild",
            "microsoft visual c++",
            "python is not set",
            "can't find python",
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
        target = self._target_for_environment(context, environment)
        result = self._run(
            context,
            target,
            [
                "install",
                "--global",
                "--no-audit",
                "--no-fund",
                root.native_specifier,
            ],
        )
        if result.returncode != 0:
            output = f"{result.stdout}\n{result.stderr}"
            if self._looks_like_native_build_failure(output):
                return OperationResult.failure(
                    "npm_native_build_prerequisite_missing",
                    "npm could not build the requested package; required native build prerequisites may be missing.",
                    data={"exit_code": result.returncode},
                )
            return OperationResult.failure(
                f"npm_package_{operation}_failed",
                f"npm {operation} failed for the exact runtime/global-prefix environment.",
                data={"exit_code": result.returncode},
            )

        self._recently_mutated[
            (environment.identity.backend_key, root.backend_key)
        ] = root.native_specifier
        return OperationResult.success(
            f"npm_package_{operation}d",
            f"npm package {operation} completed for the exact runtime/global-prefix environment.",
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
        package_name = (
            target.normalized_name
            or target.native_name
            or target.removal_key
        )
        target_runtime = self._target_for_environment(context, environment)
        result = self._run(
            context,
            target_runtime,
            ["uninstall", "--global", package_name],
        )
        if result.returncode != 0:
            return OperationResult.failure(
                "npm_package_remove_failed",
                "npm uninstall failed for the exact runtime/global-prefix environment.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "npm_package_removed",
            "npm package removal completed for the exact runtime/global-prefix environment.",
            changed=True,
        )
