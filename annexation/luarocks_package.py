"""Exact runtime-bound LuaRocks tree package backend."""

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
)
from .process import ProcessResult, run_process
from .runtime import RuntimeStateError, read_runtime_ownerships


Runner = Callable[[list[str]], ProcessResult]

_ROCK_NAME = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._-]*)(?:/[A-Za-z0-9][A-Za-z0-9._-]*)?$"
)
_LUA_LINE = re.compile(r"^(5\.[1-5])(?:\.\d+)?$")


class LuaRocksPackageEnvironmentError(RuntimeError):
    """An exact LuaRocks tree could not be addressed safely."""


@dataclass(frozen=True)
class LuaRocksTreeTarget:
    """One explicit LuaRocks tool + owned runtime + exact tree binding."""

    runtime: RuntimeInstance
    tree: Path
    luarocks: Path
    lua_version: str | None = None
    runtime_scope_subject: str | None = None
    project_owned: bool = False
    ephemeral: bool = False

    def __post_init__(self) -> None:
        if self.runtime.subject != "lua":
            raise ValueError("LuaRocks targets must bind to a Lua runtime.")
        if self.runtime.prefix is None or self.runtime.executable is None:
            raise ValueError("LuaRocks targets require exact runtime prefix and executable.")
        object.__setattr__(self, "tree", Path(self.tree))
        object.__setattr__(self, "luarocks", Path(self.luarocks))
        if self.project_owned and self.ephemeral:
            raise ValueError("A LuaRocks tree cannot be both project-owned and ephemeral.")


def normalize_rock_name(name: str) -> str:
    """Normalize a LuaRocks package or namespace/package identity."""

    value = name.strip().casefold()
    if not value or _ROCK_NAME.fullmatch(value) is None:
        raise ValueError(f"Invalid LuaRocks package name: {name!r}.")
    return value


def luarocks_desired_root(
    name: str,
    version: str | None = None,
) -> DesiredPackageRoot:
    """Create one LuaRocks-native desired root."""

    package = normalize_rock_name(name)
    exact_version = version.strip() if version is not None else None
    if exact_version == "":
        raise ValueError("LuaRocks desired version cannot be empty.")
    native = package if exact_version is None else f"{package} {exact_version}"
    metadata: dict[str, object] = {"package": package}
    if exact_version is not None:
        metadata["version"] = exact_version
    return DesiredPackageRoot(
        backend_key=package,
        native_specifier=native,
        normalized_name=package,
        metadata=metadata,
    )


class LuaRocksPackageEnvironmentBackend:
    """Current-user exact Lua runtime + rocks-tree package backend."""

    manager = "luarocks"
    name = "luarocks-exact-tree"

    def __init__(
        self,
        targets: Sequence[LuaRocksTreeTarget],
        *,
        runner: Runner | None = None,
    ) -> None:
        if not targets:
            raise ValueError("At least one explicit LuaRocks tree target is required.")
        self._targets = tuple(targets)
        self._runner = runner
        self._recently_mutated: dict[tuple[str, str], str] = {}

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if context.platform is not Platform.WINDOWS:
            raise LuaRocksPackageEnvironmentError(
                "The initial LuaRocks backend is bound to Windows Lua runtime semantics."
            )
        if not context.target_account.is_current:
            raise LuaRocksPackageEnvironmentError(
                "LuaRocks reconciliation cannot safely mutate a non-current target account."
            )

    def _scope_subject(
        self,
        context: OperationContext,
        target: LuaRocksTreeTarget,
    ) -> str | None:
        if target.runtime_scope_subject is not None:
            return target.runtime_scope_subject
        if target.runtime.backend == "machine-soul-lua-prefix":
            return f"user:{context.target_account.name.casefold()}"
        return None

    @staticmethod
    def _lua_line(target: LuaRocksTreeTarget) -> str:
        explicit = target.lua_version
        if explicit is not None:
            line = explicit.strip()
        else:
            metadata_line = target.runtime.metadata.get("lua_line")
            if isinstance(metadata_line, str) and metadata_line.strip():
                line = metadata_line.strip()
            elif target.runtime.flavor == "luajit":
                line = "5.1"
            else:
                match = _LUA_LINE.match(target.runtime.version)
                if match is None:
                    raise LuaRocksPackageEnvironmentError(
                        "Cannot derive a supported LuaRocks Lua line from the exact runtime."
                    )
                line = match.group(1)

        if re.fullmatch(r"5\.[1-5]", line) is None:
            raise LuaRocksPackageEnvironmentError(
                f"Unsupported LuaRocks Lua line {line!r}; expected 5.1 through 5.5."
            )
        return line

    @staticmethod
    def _normalized_tree(tree: Path) -> str:
        return ntpath.normcase(ntpath.normpath(str(tree)))

    def _environment(self, context: OperationContext) -> Mapping[str, str]:
        environment = dict(os.environ)
        environment.update(context.environment)
        return environment

    def _run(
        self,
        context: OperationContext,
        target: LuaRocksTreeTarget,
        args: Sequence[str],
    ) -> ProcessResult:
        assert target.runtime.prefix is not None
        argv = [
            str(target.luarocks),
            f"--lua-dir={target.runtime.prefix}",
            f"--lua-version={self._lua_line(target)}",
            f"--tree={target.tree}",
            "--no-project",
            "--deps-mode=one",
            *args,
        ]
        if self._runner is not None:
            return self._runner(argv)
        return run_process(argv, environ=self._environment(context))

    def _owned_runtime(
        self,
        context: OperationContext,
        target: LuaRocksTreeTarget,
    ) -> None:
        scope = self._scope_subject(context, target)
        try:
            ownerships = read_runtime_ownerships(context, target.runtime.subject)
        except (RuntimeStateError, ValueError) as exc:
            raise LuaRocksPackageEnvironmentError(
                f"Lua runtime provenance is invalid: {exc}"
            ) from exc
        matches = [
            state
            for state in ownerships
            if state.scope_subject == scope and state.matches_instance(target.runtime)
        ]
        if len(matches) != 1:
            raise LuaRocksPackageEnvironmentError(
                "LuaRocks tree binding requires exactly one owned exact Lua runtime."
            )

    def _backend_key(
        self,
        target: LuaRocksTreeTarget,
    ) -> str:
        return (
            f"{target.runtime.backend}:{target.runtime.backend_key}"
            f"|lua:{self._lua_line(target)}"
            f"|tree:{self._normalized_tree(target.tree)}"
        )

    def _target_for_environment(
        self,
        environment: PackageEnvironment,
    ) -> LuaRocksTreeTarget:
        matches = [
            target
            for target in self._targets
            if self._backend_key(target) == environment.identity.backend_key
        ]
        if len(matches) != 1:
            raise LuaRocksPackageEnvironmentError(
                "LuaRocks environment identity no longer maps to exactly one configured target."
            )
        return matches[0]

    def discover_environments(
        self,
        context: OperationContext,
    ) -> tuple[PackageEnvironment, ...]:
        self._guard_context(context)
        environments: list[PackageEnvironment] = []
        seen_keys: set[str] = set()
        seen_trees: dict[str, str] = {}

        for target in self._targets:
            self._owned_runtime(context, target)
            if not target.tree.is_dir():
                raise LuaRocksPackageEnvironmentError(
                    f"Configured LuaRocks tree does not exist: {target.tree!s}."
                )

            tree_key = self._normalized_tree(target.tree)
            runtime_key = (
                f"{target.runtime.backend}:{target.runtime.backend_key}:"
                f"{self._lua_line(target)}"
            )
            previous = seen_trees.get(tree_key)
            if previous is not None and previous != runtime_key:
                raise LuaRocksPackageEnvironmentError(
                    "One physical LuaRocks tree cannot be shared across exact Lua runtimes."
                )
            seen_trees[tree_key] = runtime_key

            backend_key = self._backend_key(target)
            if backend_key in seen_keys:
                raise LuaRocksPackageEnvironmentError(
                    "Duplicate LuaRocks targets resolve to the same exact environment."
                )
            seen_keys.add(backend_key)

            if target.project_owned:
                observed_ownership = PackageEnvironmentOwnershipKind.PROJECT_OWNED
                classification = "project-rocks-tree"
            elif target.ephemeral:
                observed_ownership = PackageEnvironmentOwnershipKind.EPHEMERAL_UNMANAGED
                classification = "ephemeral-rocks-tree"
            else:
                observed_ownership = PackageEnvironmentOwnershipKind.UNMANAGED
                classification = "runtime-rocks-tree"

            runtime_ref = RuntimeInstanceRef.from_instance(
                target.runtime,
                scope_subject=self._scope_subject(context, target),
            )
            identity = PackageEnvironmentIdentity(
                manager=self.manager,
                backend=self.name,
                backend_key=backend_key,
                locator=PackageEnvironmentLocator(
                    "luarocks-tree",
                    {
                        "luarocks": str(target.luarocks),
                        "lua_dir": str(target.runtime.prefix),
                        "lua_version": self._lua_line(target),
                        "tree": str(target.tree),
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
                        "runtime_version": target.runtime.version,
                        "runtime_flavor": target.runtime.flavor or "",
                        "tree": str(target.tree),
                        "lua_version": self._lua_line(target),
                    },
                )
            )

        return tuple(environments)

    def check_tool(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> OperationResult:
        target = self._target_for_environment(environment)
        result = self._run(context, target, ["--version"])
        if result.returncode != 0:
            return OperationResult.failure(
                "luarocks_tool_unavailable",
                "LuaRocks is not available for the exact target binding.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "luarocks_tool_available",
            "LuaRocks is available for the exact target binding.",
            data={"version_output": result.stdout.strip()[:200]},
        )

    @staticmethod
    def _observed_key(name: str, version: str, arch: str) -> str:
        return json.dumps(
            ["rock", name, version, arch],
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _removal_key(name: str, version: str) -> str:
        return json.dumps(
            [name, version],
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _parse_removal_key(value: str) -> tuple[str, str]:
        try:
            payload = json.loads(value)
        except json.JSONDecodeError as exc:
            raise LuaRocksPackageEnvironmentError(
                "Persisted LuaRocks removal identity is malformed."
            ) from exc
        if (
            not isinstance(payload, list)
            or len(payload) != 2
            or not all(isinstance(item, str) and item for item in payload)
        ):
            raise LuaRocksPackageEnvironmentError(
                "Persisted LuaRocks removal identity has an invalid shape."
            )
        return normalize_rock_name(payload[0]), payload[1]

    def _list_rows(
        self,
        context: OperationContext,
        target: LuaRocksTreeTarget,
    ) -> list[tuple[str, str, str, str, str | None]]:
        result = self._run(context, target, ["list", "--porcelain"])
        if result.returncode != 0:
            raise LuaRocksPackageEnvironmentError(
                f"LuaRocks list failed with exit code {result.returncode}."
            )

        rows: list[tuple[str, str, str, str, str | None]] = []
        for raw_line in result.stdout.splitlines():
            if not raw_line.strip():
                continue
            columns = raw_line.split("\t")
            if len(columns) not in {4, 5}:
                raise LuaRocksPackageEnvironmentError(
                    "LuaRocks porcelain inventory returned an unexpected column count."
                )
            name, version, arch, repository = columns[:4]
            namespace = columns[4].strip() if len(columns) == 5 else ""
            if not all(item.strip() for item in (name, version, arch, repository)):
                raise LuaRocksPackageEnvironmentError(
                    "LuaRocks porcelain inventory contains empty required fields."
                )
            full_name = (
                f"{namespace}/{name}" if namespace else name
            )
            rows.append(
                (
                    normalize_rock_name(full_name),
                    version.strip(),
                    arch.strip(),
                    repository.strip(),
                    namespace or None,
                )
            )
        return rows

    @staticmethod
    def _dependency_name(line: str) -> str | None:
        value = line.strip()
        if not value:
            return None
        token = value.split(None, 1)[0]
        try:
            normalized = normalize_rock_name(token)
        except ValueError:
            return None
        if normalized == "lua":
            return None
        return normalized

    def _dependencies_for(
        self,
        context: OperationContext,
        target: LuaRocksTreeTarget,
        name: str,
        version: str,
    ) -> set[str]:
        result = self._run(
            context,
            target,
            ["show", name, version, "--deps"],
        )
        if result.returncode != 0:
            raise LuaRocksPackageEnvironmentError(
                f"LuaRocks dependency discovery failed for {name} {version}."
            )
        dependencies: set[str] = set()
        for line in result.stdout.splitlines():
            dependency = self._dependency_name(line)
            if dependency is not None:
                dependencies.add(dependency)
        return dependencies

    def discover_inventory(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PackageInventory:
        target = self._target_for_environment(environment)
        rows = self._list_rows(context, target)
        dependency_names: set[str] = set()
        for name, version, _arch, _repository, _namespace in rows:
            dependency_names.update(
                self._dependencies_for(context, target, name, version)
            )

        packages: list[ObservedPackage] = []
        seen: set[str] = set()
        for name, version, arch, repository, namespace in rows:
            backend_key = self._observed_key(name, version, arch)
            if backend_key in seen:
                raise LuaRocksPackageEnvironmentError(
                    "LuaRocks inventory contains a duplicate exact rock identity."
                )
            seen.add(backend_key)
            metadata: dict[str, object] = {
                "arch": arch,
                "repository": repository,
            }
            if namespace is not None:
                metadata["namespace"] = namespace
            packages.append(
                ObservedPackage(
                    backend_key=backend_key,
                    native_name=name,
                    version=version,
                    kind=(
                        PackageObservationKind.TRANSITIVE
                        if name in dependency_names
                        else PackageObservationKind.TOP_LEVEL
                    ),
                    normalized_name=name,
                    metadata=metadata,
                )
            )

        return PackageInventory(environment.identity.backend_key, tuple(packages))

    @staticmethod
    def _desired_parts(root: DesiredPackageRoot) -> tuple[str, str | None]:
        package = root.metadata.get("package")
        version = root.metadata.get("version")
        if not isinstance(package, str) or normalize_rock_name(package) != root.backend_key:
            raise LuaRocksPackageEnvironmentError(
                "LuaRocks desired root metadata does not match its exact package key."
            )
        if version is not None and (not isinstance(version, str) or not version.strip()):
            raise LuaRocksPackageEnvironmentError(
                "LuaRocks desired root version metadata is invalid."
            )
        return package, version

    @staticmethod
    def _candidates(
        inventory: PackageInventory,
        name: str,
    ) -> list[ObservedPackage]:
        return [
            package
            for package in inventory.packages
            if package.normalized_name == name
        ]

    def verify(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        desired_roots: Sequence[DesiredPackageRoot],
        inventory: PackageInventory,
        owned_roots: Sequence[PackageRootOwnership],
    ) -> PackageVerification:
        del context
        owned_by_key = {root.backend_key: root for root in owned_roots}
        resolutions: list[PackageRootResolution] = []

        for root in desired_roots:
            name, version = self._desired_parts(root)
            candidates = self._candidates(inventory, name)
            by_observed = {item.backend_key: item for item in candidates}
            owned = owned_by_key.get(root.backend_key)
            recently_verified = (
                self._recently_mutated.get(
                    (environment.identity.backend_key, root.backend_key)
                )
                == root.native_specifier
            )

            selected: ObservedPackage | None = None
            if (
                owned is not None
                and owned.native_specifier == root.native_specifier
                and owned.observed_key in by_observed
            ):
                selected = by_observed[owned.observed_key]
            elif version is not None:
                selected = next(
                    (item for item in candidates if item.version == version),
                    None,
                )
            elif candidates:
                selected = candidates[0]

            if selected is not None and (
                recently_verified
                or version is None
                or selected.version == version
                or (
                    owned is not None
                    and owned.native_specifier == root.native_specifier
                    and owned.observed_key == selected.backend_key
                )
            ):
                assert selected.version is not None
                resolutions.append(
                    PackageRootResolution(
                        root.backend_key,
                        PackageRootStatus.SATISFIED,
                        observed_key=selected.backend_key,
                        removal_key=self._removal_key(name, selected.version),
                    )
                )
                continue

            if candidates:
                existing = candidates[0]
                assert existing.version is not None
                resolutions.append(
                    PackageRootResolution(
                        root.backend_key,
                        PackageRootStatus.UPDATE_REQUIRED,
                        observed_key=existing.backend_key,
                        removal_key=self._removal_key(name, existing.version),
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
    def _looks_like_native_prerequisite_failure(output: str) -> bool:
        lowered = output.casefold()
        indicators = (
            "lua.h",
            "lua_incdir",
            "lua_libdir",
            "external dependency",
            "could not find library",
            "no compiler",
            "compiler not found",
            "gcc: command not found",
            "cl is not recognized",
            "microsoft visual c++",
            "mingw",
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
        target = self._target_for_environment(environment)
        name, version = self._desired_parts(root)
        args = ["install", name]
        if version is not None:
            args.append(version)
        result = self._run(context, target, args)
        if result.returncode != 0:
            output = f"{result.stdout}\n{result.stderr}"
            if self._looks_like_native_prerequisite_failure(output):
                return OperationResult.failure(
                    "luarocks_native_build_prerequisite_missing",
                    "LuaRocks could not build the requested rock because a native/Lua prerequisite is missing.",
                    data={"exit_code": result.returncode},
                )
            return OperationResult.failure(
                f"luarocks_package_{operation}_failed",
                f"LuaRocks {operation} failed for the exact runtime-bound tree.",
                data={"exit_code": result.returncode},
            )

        self._recently_mutated[
            (environment.identity.backend_key, root.backend_key)
        ] = root.native_specifier
        return OperationResult.success(
            f"luarocks_package_{operation}d",
            f"LuaRocks package {operation} completed for the exact runtime-bound tree.",
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
        rock_target = self._target_for_environment(environment)
        name, version = self._parse_removal_key(target.removal_key)
        result = self._run(
            context,
            rock_target,
            ["remove", name, version],
        )
        if result.returncode != 0:
            return OperationResult.failure(
                "luarocks_package_remove_failed",
                "LuaRocks remove failed for the exact runtime-bound tree.",
                data={"exit_code": result.returncode},
            )
        return OperationResult.success(
            "luarocks_package_removed",
            "LuaRocks package removal completed for the exact runtime-bound tree.",
            changed=True,
        )
