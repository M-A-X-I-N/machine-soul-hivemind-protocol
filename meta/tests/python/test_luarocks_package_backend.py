from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation.luarocks_package import (
    LuaRocksPackageEnvironmentBackend,
    LuaRocksPackageEnvironmentError,
    LuaRocksTreeTarget,
    luarocks_desired_root,
)
from annexation.model import (
    OperationContext,
    PackageEnvironmentDesiredState,
    PackageEnvironmentOwnershipKind,
    PackageMutationPolicy,
    Platform,
    RuntimeInstance,
    RuntimeOwnership,
    TargetAccount,
)
from annexation.package_environment import (
    adopt_package_environment,
    package_environment_runtime_removal_guard,
    reconcile_package_environment,
)
from annexation.process import ProcessResult
from annexation.runtime import runtime_ownership_path
from annexation.state import write_json_state


class FakeLuaRocksRunner:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.packages: dict[str, dict[str, dict[str, object]]] = {}
        self.install_dependencies: dict[str, dict[str, str]] = {}
        self.native_failure = False

    @staticmethod
    def _tree(argv: list[str]) -> str:
        return next(item.split("=", 1)[1] for item in argv if item.startswith("--tree="))

    @staticmethod
    def _command(argv: list[str]) -> list[str]:
        binding_flags = (
            "--lua-dir=",
            "--lua-version=",
            "--tree=",
            "--no-project",
            "--deps-mode=",
        )
        index = 1
        while index < len(argv):
            value = argv[index]
            if any(
                value == prefix or value.startswith(prefix)
                for prefix in binding_flags
            ):
                index += 1
                continue
            break
        return argv[index:]

    def add_tree(self, tree: str) -> None:
        self.packages.setdefault(tree, {})

    def add_package(
        self,
        tree: str,
        name: str,
        version: str,
        *,
        dependencies: dict[str, str] | None = None,
    ) -> None:
        self.packages[tree][name.casefold()] = {
            "name": name.casefold(),
            "version": version,
            "dependencies": dict(dependencies or {}),
        }

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        tree = self._tree(argv)
        command = self._command(argv)
        self.packages.setdefault(tree, {})

        if command == ["--version"]:
            return ProcessResult(0, "LuaRocks 3.13.0\n", "")

        if command == ["list", "--porcelain"]:
            lines = []
            for package in sorted(
                self.packages[tree].values(),
                key=lambda item: str(item["name"]),
            ):
                lines.append(
                    "\t".join(
                        (
                            str(package["name"]),
                            str(package["version"]),
                            "installed",
                            f"{tree}/lib/luarocks/rocks",
                        )
                    )
                )
            return ProcessResult(0, "\n".join(lines) + ("\n" if lines else ""), "")

        if len(command) >= 4 and command[0] == "show" and command[-1] == "--deps":
            name = command[1].casefold()
            version = command[2]
            package = self.packages[tree].get(name)
            if package is None or package["version"] != version:
                return ProcessResult(1, "", "rock not found")
            deps = package["dependencies"]
            assert isinstance(deps, dict)
            lines = [
                f"{dep} >= {dep_version}"
                for dep, dep_version in sorted(deps.items())
            ]
            lines.insert(0, "lua >= 5.1")
            return ProcessResult(0, "\n".join(lines) + "\n", "")

        if command and command[0] == "install":
            if self.native_failure:
                return ProcessResult(
                    1,
                    "",
                    "Error: Failed finding Lua header lua.h; no compiler available",
                )
            name = command[1].casefold()
            version = command[2] if len(command) > 2 else "1.0-1"
            dependencies = self.install_dependencies.get(name, {})
            self.add_package(
                tree,
                name,
                version,
                dependencies=dependencies,
            )
            for dep, dep_version in dependencies.items():
                if dep.casefold() not in self.packages[tree]:
                    self.add_package(tree, dep, dep_version)
            return ProcessResult(0, "installed", "")

        if command and command[0] == "remove":
            name = command[1].casefold()
            version = command[2]
            package = self.packages[tree].get(name)
            if package is None or package["version"] != version:
                return ProcessResult(1, "", "rock not found")
            self.packages[tree].pop(name)
            return ProcessResult(0, "removed", "")

        return ProcessResult(99, "", f"unexpected fake command: {argv!r}")


class LuaRocksPackageBackendTests(unittest.TestCase):
    def context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount(
                "fixture",
                root / "fixture",
                True,
                local_app_data=root / "fixture" / "AppData" / "Local",
            ),
        )

    @staticmethod
    def runtime(
        version: str,
        prefix: Path,
        *,
        flavor: str = "puc",
        backend_key: str | None = None,
    ) -> RuntimeInstance:
        line = ".".join(version.split(".")[:2]) if flavor == "puc" else None
        metadata = {
            "executable_name": (
                f"lua{line.replace('.', '')}.exe"
                if line is not None
                else "luajit.exe"
            )
        }
        if line is not None:
            metadata["lua_line"] = line
        return RuntimeInstance(
            subject="lua",
            version=version,
            backend="machine-soul-lua-prefix",
            backend_key=backend_key or f"{flavor}:{version}:x64",
            architecture="x64",
            flavor=flavor,
            distribution="lua.org" if flavor == "puc" else "luajit.org",
            executable=prefix / str(metadata["executable_name"]),
            prefix=prefix,
            metadata=metadata,
        )

    @staticmethod
    def own_runtime(
        context: OperationContext,
        runtime: RuntimeInstance,
    ) -> None:
        scope = f"user:{context.target_account.name.casefold()}"
        ownership = RuntimeOwnership.from_instance(
            context.host,
            runtime,
            scope_subject=scope,
        )
        write_json_state(
            runtime_ownership_path(
                context,
                runtime.subject,
                runtime.backend,
                runtime.backend_key,
                scope_subject=scope,
            ),
            ownership.to_dict(),
        )

    @staticmethod
    def assert_exact_binding(call: list[str], target: LuaRocksTreeTarget) -> None:
        assert target.runtime.prefix is not None
        line = (
            str(target.runtime.metadata["lua_line"])
            if "lua_line" in target.runtime.metadata
            else "5.1"
        )
        expected = {
            f"--lua-dir={target.runtime.prefix}",
            f"--lua-version={line}",
            f"--tree={target.tree}",
            "--no-project",
            "--deps-mode=one",
        }
        assert expected.issubset(set(call))

    def test_two_runtime_trees_isolate_overlapping_rocks_and_transitives(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree51 = root / "rocks51"
            tree54 = root / "rocks54"
            tree51.mkdir()
            tree54.mkdir()
            runtime51 = self.runtime("5.1.5", root / "lua51")
            runtime54 = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime51)
            self.own_runtime(context, runtime54)
            target51 = LuaRocksTreeTarget(runtime51, tree51, Path("C:/tools/luarocks.exe"))
            target54 = LuaRocksTreeTarget(runtime54, tree54, Path("C:/tools/luarocks.exe"))
            runner.add_tree(str(tree51))
            runner.add_tree(str(tree54))
            runner.add_package(
                str(tree51),
                "shared-rock",
                "1.0-1",
                dependencies={"dep-rock": "1.0-1"},
            )
            runner.add_package(str(tree51), "dep-rock", "1.0-1")
            runner.add_package(str(tree54), "shared-rock", "2.0-1")
            backend = LuaRocksPackageEnvironmentBackend(
                [target51, target54],
                runner=runner,
            )

            environments = backend.discover_environments(context)
            inventories = {
                env.identity.runtime.backend_key: backend.discover_inventory(context, env)
                for env in environments
                if env.identity.runtime is not None
            }

        self.assertEqual(2, len(environments))
        self.assertNotEqual(
            environments[0].identity.backend_key,
            environments[1].identity.backend_key,
        )
        versions = {
            key: next(
                item.version
                for item in inventory.packages
                if item.normalized_name == "shared-rock"
            )
            for key, inventory in inventories.items()
        }
        self.assertEqual("1.0-1", versions[runtime51.backend_key])
        self.assertEqual("2.0-1", versions[runtime54.backend_key])
        inventory51 = inventories[runtime51.backend_key]
        kinds = {item.normalized_name: item.kind.value for item in inventory51.packages}
        self.assertEqual("top_level", kinds["shared-rock"])
        self.assertEqual("transitive", kinds["dep-rock"])
        for call in runner.calls:
            if f"--tree={tree51}" in call:
                self.assert_exact_binding(call, target51)
            elif f"--tree={tree54}" in call:
                self.assert_exact_binding(call, target54)

    def test_reconcile_preserves_unknown_root_and_blocks_runtime_removal(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "rocks54"
            tree.mkdir()
            runtime = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime)
            target = LuaRocksTreeTarget(runtime, tree, Path("C:/tools/luarocks.exe"))
            runner.add_tree(str(tree))
            runner.add_package(str(tree), "human-rock", "7.0-1")
            runner.install_dependencies["managed-rock"] = {"managed-dep": "1.0-1"}
            backend = LuaRocksPackageEnvironmentBackend([target], runner=runner)

            environment = backend.discover_environments(context)[0]
            adopted = adopt_package_environment(
                context,
                backend,
                environment.identity.backend_key,
                mutation_policy=PackageMutationPolicy.MANAGED_ROOTS,
            )
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (luarocks_desired_root("managed-rock", "2.0-1"),),
            )
            reconciled = reconcile_package_environment(context, backend, desired)
            final_inventory = backend.discover_inventory(context, environment)
            guard = package_environment_runtime_removal_guard(
                context,
                runtime,
                scope_subject="user:fixture",
            )

        self.assertEqual("package_environment_owned", adopted.code)
        self.assertEqual("package_environment_reconciled", reconciled.code)
        self.assertIn("human-rock", runner.packages[str(tree)])
        self.assertEqual("2.0-1", runner.packages[str(tree)]["managed-rock"]["version"])
        self.assertEqual("runtime_has_owned_package_environments", guard.code)
        kinds = {item.normalized_name: item.kind.value for item in final_inventory.packages}
        self.assertEqual("top_level", kinds["human-rock"])
        self.assertEqual("top_level", kinds["managed-rock"])
        self.assertEqual("transitive", kinds["managed-dep"])

    def test_owned_root_removal_is_exact_to_one_runtime_tree(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree51 = root / "rocks51"
            tree54 = root / "rocks54"
            tree51.mkdir()
            tree54.mkdir()
            runtime51 = self.runtime("5.1.5", root / "lua51")
            runtime54 = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime51)
            self.own_runtime(context, runtime54)
            target51 = LuaRocksTreeTarget(runtime51, tree51, Path("C:/tools/luarocks.exe"))
            target54 = LuaRocksTreeTarget(runtime54, tree54, Path("C:/tools/luarocks.exe"))
            runner.add_tree(str(tree51))
            runner.add_tree(str(tree54))
            runner.add_package(str(tree51), "managed-rock", "1.0-1")
            runner.add_package(str(tree54), "managed-rock", "9.0-1")
            backend = LuaRocksPackageEnvironmentBackend(
                [target51, target54],
                runner=runner,
            )

            environment51 = next(
                env
                for env in backend.discover_environments(context)
                if env.identity.runtime is not None
                and env.identity.runtime.backend_key == runtime51.backend_key
            )
            adopt_package_environment(
                context,
                backend,
                environment51.identity.backend_key,
                mutation_policy=PackageMutationPolicy.MANAGED_ROOTS,
            )
            desired = PackageEnvironmentDesiredState(
                environment51.identity,
                (luarocks_desired_root("managed-rock", "1.0-1"),),
            )
            first = reconcile_package_environment(context, backend, desired)
            empty = PackageEnvironmentDesiredState(environment51.identity, ())
            removed = reconcile_package_environment(context, backend, empty)

        self.assertEqual("package_environment_reconciled", first.code)
        self.assertEqual("package_environment_reconciled", removed.code)
        self.assertNotIn("managed-rock", runner.packages[str(tree51)])
        self.assertEqual("9.0-1", runner.packages[str(tree54)]["managed-rock"]["version"])
        remove_calls = [
            call
            for call in runner.calls
            if runner._command(call)[:1] == ["remove"]
        ]
        self.assertEqual(1, len(remove_calls))
        self.assertIn(f"--tree={tree51}", remove_calls[0])

    def test_project_tree_is_not_adoptable_without_explicit_reclassification(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "project" / "lua_modules"
            tree.mkdir(parents=True)
            runtime = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime)
            target = LuaRocksTreeTarget(
                runtime,
                tree,
                Path("C:/tools/luarocks.exe"),
                project_owned=True,
            )
            runner.add_tree(str(tree))
            backend = LuaRocksPackageEnvironmentBackend([target], runner=runner)

            environment = backend.discover_environments(context)[0]
            result = adopt_package_environment(
                context,
                backend,
                environment.identity.backend_key,
            )

        self.assertEqual(
            PackageEnvironmentOwnershipKind.PROJECT_OWNED,
            environment.ownership,
        )
        self.assertEqual("package_environment_not_adoptable", result.code)

    def test_unowned_runtime_binding_is_refused(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "rocks54"
            tree.mkdir()
            runtime = self.runtime("5.4.8", root / "lua54")
            target = LuaRocksTreeTarget(runtime, tree, Path("C:/tools/luarocks.exe"))
            backend = LuaRocksPackageEnvironmentBackend([target], runner=runner)

            with self.assertRaises(LuaRocksPackageEnvironmentError):
                backend.discover_environments(context)

    def test_one_tree_cannot_be_shared_between_runtime_versions(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "rocks"
            tree.mkdir()
            runtime51 = self.runtime("5.1.5", root / "lua51")
            runtime54 = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime51)
            self.own_runtime(context, runtime54)
            backend = LuaRocksPackageEnvironmentBackend(
                [
                    LuaRocksTreeTarget(runtime51, tree, Path("C:/tools/luarocks.exe")),
                    LuaRocksTreeTarget(runtime54, tree, Path("C:/tools/luarocks.exe")),
                ],
                runner=runner,
            )

            with self.assertRaises(LuaRocksPackageEnvironmentError):
                backend.discover_environments(context)

    def test_luajit_defaults_to_lua_51_binding(self):
        runner = FakeLuaRocksRunner()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "rocks-jit"
            tree.mkdir()
            runtime = self.runtime(
                "2.1.0-beta3",
                root / "luajit",
                flavor="luajit",
                backend_key="luajit:2.1.0-beta3:x64",
            )
            self.own_runtime(context, runtime)
            target = LuaRocksTreeTarget(runtime, tree, Path("C:/tools/luarocks.exe"))
            runner.add_tree(str(tree))
            backend = LuaRocksPackageEnvironmentBackend([target], runner=runner)

            environment = backend.discover_environments(context)
            self.assertEqual(1, len(environment))
            tool = backend.check_tool(context, environment[0])

        self.assertEqual("luarocks_tool_available", tool.code)
        self.assertTrue(runner.calls)
        self.assertTrue(all("--lua-version=5.1" in call for call in runner.calls))

    def test_native_build_failure_is_explicit_and_no_toolchain_is_installed(self):
        runner = FakeLuaRocksRunner()
        runner.native_failure = True
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            context = self.context(root)
            tree = root / "rocks54"
            tree.mkdir()
            runtime = self.runtime("5.4.8", root / "lua54")
            self.own_runtime(context, runtime)
            target = LuaRocksTreeTarget(runtime, tree, Path("C:/tools/luarocks.exe"))
            runner.add_tree(str(tree))
            backend = LuaRocksPackageEnvironmentBackend([target], runner=runner)

            environment = backend.discover_environments(context)[0]
            result = backend.install(
                context,
                environment,
                luarocks_desired_root("native-rock", "1.0-1"),
            )

        self.assertEqual("luarocks_native_build_prerequisite_missing", result.code)
        self.assertEqual(1, result.data["exit_code"])

    def test_desired_root_and_exact_remove_identity(self):
        root = luarocks_desired_root("My_Rock", "1.2-3")
        self.assertEqual("my_rock", root.backend_key)
        self.assertEqual("my_rock 1.2-3", root.native_specifier)


if __name__ == "__main__":
    unittest.main()
