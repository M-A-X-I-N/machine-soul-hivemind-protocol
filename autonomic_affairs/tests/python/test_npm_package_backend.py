from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    OperationContext,
    PackageEnvironmentDesiredState,
    PackageMutationPolicy,
    Platform,
    RuntimeInstance,
    TargetAccount,
)
from annexation_procedures.npm_package import (
    NpmGlobalPackageEnvironmentBackend,
    NpmGlobalTarget,
    normalize_npm_package_name,
    npm_desired_root,
)
from annexation_procedures.package_environment import (
    adopt_package_environment,
    package_environment_runtime_removal_guard,
    reconcile_package_environment,
)
from annexation_procedures.process import ProcessResult


class FakeNpmRunner:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.prefixes: dict[str, str] = {}
        self.roots: dict[str, str] = {}
        self.packages: dict[str, dict[str, dict[str, object]]] = {}
        self.native_failure = False

    def add_runtime(self, node: str, prefix: str) -> None:
        self.prefixes[node] = prefix
        self.roots[node] = f"{prefix}/node_modules"
        self.packages.setdefault(node, {})

    def add_package(
        self,
        node: str,
        name: str,
        version: str,
        *,
        dependencies: dict[str, tuple[str, dict]] | None = None,
    ) -> None:
        self.packages[node][normalize_npm_package_name(name)] = {
            "name": name,
            "version": version,
            "dependencies": dependencies or {},
        }

    @staticmethod
    def _name_and_version(specifier: str) -> tuple[str, str | None]:
        value = specifier.strip()
        if value.startswith("@"):
            slash = value.find("/")
            version_at = value.find("@", slash + 1)
            name = value if version_at < 0 else value[:version_at]
            version = None if version_at < 0 else value[version_at + 1 :]
        else:
            version_at = value.find("@", 1)
            name = value if version_at < 0 else value[:version_at]
            version = None if version_at < 0 else value[version_at + 1 :]
        return normalize_npm_package_name(name), (version or None)

    @staticmethod
    def _node_json(package: dict[str, object]) -> dict[str, object]:
        result: dict[str, object] = {"version": package["version"]}
        dependencies = package.get("dependencies", {})
        if dependencies:
            result["dependencies"] = {
                child_name: {
                    "version": child_version,
                    "dependencies": child_dependencies,
                }
                for child_name, (child_version, child_dependencies) in dependencies.items()
            }
        return result

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        node = argv[0]
        args = argv[2:]

        if args == ["prefix", "--global"]:
            return ProcessResult(0, self.prefixes[node] + "\n", "")
        if args == ["root", "--global"]:
            return ProcessResult(0, self.roots[node] + "\n", "")
        if args == ["--version"]:
            return ProcessResult(0, "12.0.1\n", "")

        if args[:4] == ["ls", "--global", "--all", "--json"]:
            payload = {
                "dependencies": {
                    package["name"]: self._node_json(package)
                    for package in self.packages[node].values()
                }
            }
            return ProcessResult(0, json.dumps(payload), "")

        if (
            len(args) >= 5
            and args[:3] == ["ls", "--global", "--depth=0"]
            and args[3] == "--json"
        ):
            name, requested_version = self._name_and_version(args[4])
            package = self.packages[node].get(name)
            satisfied = package is not None and (
                requested_version is None
                or requested_version in {"*", "latest"}
                or package["version"] == requested_version
            )
            if satisfied:
                payload = {
                    "dependencies": {
                        package["name"]: self._node_json(package)
                    }
                }
                return ProcessResult(0, json.dumps(payload), "")
            return ProcessResult(
                1,
                json.dumps({"dependencies": {}}),
                "npm error code ELSPROBLEMS",
            )

        if args and args[0] == "install" and "--global" in args:
            if self.native_failure:
                return ProcessResult(
                    1,
                    "",
                    "npm error node-gyp gyp ERR! find VS could not find Visual Studio",
                )
            specifier = args[-1]
            name, requested_version = self._name_and_version(specifier)
            self.packages[node][name] = {
                "name": name,
                "version": requested_version or "1.0.0",
                "dependencies": {
                    f"dep-{name}": ("1.0.0", {}),
                },
            }
            return ProcessResult(0, "added", "")

        if args and args[0] == "uninstall" and "--global" in args:
            name = normalize_npm_package_name(args[-1])
            self.packages[node].pop(name, None)
            return ProcessResult(0, "removed", "")

        return ProcessResult(99, "", f"unexpected fake command: {argv!r}")


class NpmPackageBackendTests(unittest.TestCase):
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
    def runtime(version: str, prefix: str) -> RuntimeInstance:
        return RuntimeInstance(
            subject="node",
            version=version,
            backend="nvm-windows-v2",
            backend_key=version,
            architecture="x64",
            distribution="nodejs",
            executable=Path(f"{prefix}/node.exe"),
            prefix=Path(prefix),
            metadata={"bundled_npm_version": "12.0.1"},
        )

    def test_desired_root_handles_scoped_and_unscoped_names(self):
        plain = npm_desired_root("TypeScript@6.0.0")
        scoped = npm_desired_root("@scope/tool@2.0.0")
        self.assertEqual("typescript", plain.backend_key)
        self.assertEqual("@scope/tool", scoped.backend_key)

    def test_two_runtime_prefixes_keep_global_inventory_separate(self):
        runner = FakeNpmRunner()
        runtime22 = self.runtime("22.20.0", "C:/nvm/v22.20.0")
        runtime24 = self.runtime("24.9.0", "C:/nvm/v24.9.0")
        runner.add_runtime(str(runtime22.executable), "C:/prefix/node22")
        runner.add_runtime(str(runtime24.executable), "C:/prefix/node24")
        runner.add_package(str(runtime22.executable), "shared-cli", "1.0.0")
        runner.add_package(str(runtime24.executable), "shared-cli", "2.0.0")
        backend = NpmGlobalPackageEnvironmentBackend(
            [NpmGlobalTarget(runtime22), NpmGlobalTarget(runtime24)],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
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
            key: inventory.packages[0].version
            for key, inventory in inventories.items()
        }
        self.assertEqual("1.0.0", versions["22.20.0"])
        self.assertEqual("2.0.0", versions["24.9.0"])

    def test_reconcile_preserves_unknown_root_and_observes_transitives(self):
        runner = FakeNpmRunner()
        runtime = self.runtime("24.9.0", "C:/nvm/v24.9.0")
        node = str(runtime.executable)
        runner.add_runtime(node, "C:/prefix/node24")
        runner.add_package(
            node,
            "human-cli",
            "7.0.0",
            dependencies={"human-dep": ("1.0.0", {})},
        )
        backend = NpmGlobalPackageEnvironmentBackend(
            [NpmGlobalTarget(runtime)],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            adopted = adopt_package_environment(
                context,
                backend,
                environment.identity.backend_key,
                mutation_policy=PackageMutationPolicy.MANAGED_ROOTS,
            )
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (npm_desired_root("managed-cli@2.0.0"),),
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
        self.assertIn("human-cli", runner.packages[node])
        self.assertEqual("2.0.0", runner.packages[node]["managed-cli"]["version"])
        self.assertEqual("runtime_has_owned_package_environments", guard.code)
        kinds = {item.native_name: item.kind.value for item in final_inventory.packages}
        self.assertEqual("top_level", kinds["human-cli"])
        self.assertEqual("transitive", kinds["human-dep"])
        self.assertEqual("top_level", kinds["managed-cli"])
        self.assertEqual("transitive", kinds["dep-managed-cli"])

    def test_every_global_operation_uses_exact_node_and_npm_cli(self):
        runner = FakeNpmRunner()
        runtime = self.runtime("24.9.0", "C:/nvm/v24.9.0")
        node = str(runtime.executable)
        runner.add_runtime(node, "C:/prefix/node24")
        explicit_cli = Path("C:/nvm/v24.9.0/custom/npm-cli.js")
        backend = NpmGlobalPackageEnvironmentBackend(
            [NpmGlobalTarget(runtime, npm_cli=explicit_cli)],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            backend.check_tool(context, environment)
            backend.discover_inventory(context, environment)

        self.assertTrue(runner.calls)
        for call in runner.calls:
            self.assertEqual(node, call[0])
            self.assertEqual(str(explicit_cli), call[1])
        global_commands = [
            call[2:]
            for call in runner.calls
            if call[2:] != ["--version"]
        ]
        self.assertTrue(
            all("--global" in command for command in global_commands)
        )

    def test_persisted_root_provenance_avoids_spec_probe(self):
        runner = FakeNpmRunner()
        runtime = self.runtime("24.9.0", "C:/nvm/v24.9.0")
        node = str(runtime.executable)
        runner.add_runtime(node, "C:/prefix/node24")
        target = NpmGlobalTarget(runtime)

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            first = NpmGlobalPackageEnvironmentBackend([target], runner=runner)
            environment = first.discover_environments(context)[0]
            adopt_package_environment(context, first, environment.identity.backend_key)
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (npm_desired_root("demo-cli@1.0.0"),),
            )
            first_result = reconcile_package_environment(context, first, desired)
            self.assertEqual("package_environment_reconciled", first_result.code)

            runner.calls.clear()
            recovered = NpmGlobalPackageEnvironmentBackend([target], runner=runner)
            second_result = reconcile_package_environment(context, recovered, desired)

        self.assertEqual("package_environment_reconciled", second_result.code)
        spec_queries = [
            call for call in runner.calls
            if call[2:5] == ["ls", "--global", "--depth=0"]
        ]
        self.assertEqual([], spec_queries)

    def test_native_build_failure_is_explicit_and_does_not_annex_toolchain(self):
        runner = FakeNpmRunner()
        runtime = self.runtime("24.9.0", "C:/nvm/v24.9.0")
        node = str(runtime.executable)
        runner.add_runtime(node, "C:/prefix/node24")
        runner.native_failure = True
        backend = NpmGlobalPackageEnvironmentBackend(
            [NpmGlobalTarget(runtime)],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            result = backend.install(
                context,
                environment,
                npm_desired_root("native-cli@1.0.0"),
            )

        self.assertEqual("npm_native_build_prerequisite_missing", result.code)
        self.assertEqual(1, result.data["exit_code"])


if __name__ == "__main__":
    unittest.main()
