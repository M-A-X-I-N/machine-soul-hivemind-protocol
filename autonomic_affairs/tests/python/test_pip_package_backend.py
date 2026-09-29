from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    OperationContext,
    PackageEnvironmentDesiredState,
    PackageEnvironmentOwnershipKind,
    PackageMutationPolicy,
    Platform,
    RuntimeInstance,
    TargetAccount,
)
from annexation_procedures.package_environment import (
    adopt_package_environment,
    package_environment_runtime_removal_guard,
    reconcile_package_environment,
)
from annexation_procedures.pip_package import (
    PipEnvironmentTarget,
    PipPackageEnvironmentBackend,
    normalize_python_distribution_name,
    pip_desired_root,
)
from annexation_procedures.process import ProcessResult


class FakePipRunner:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.probes: dict[str, dict[str, object]] = {}
        self.packages: dict[str, dict[str, dict[str, object]]] = {}
        self.inherited_packages: dict[str, dict[str, str]] = {}
        self.native_failure = False

    @staticmethod
    def _interpreter_key(interpreter: str) -> str:
        return str(Path(interpreter))

    def add_environment(
        self,
        interpreter: str,
        *,
        prefix: str,
        base_prefix: str | None = None,
        externally_managed: bool = False,
    ) -> None:
        base = base_prefix or prefix
        interpreter = self._interpreter_key(interpreter)
        self.probes[interpreter] = {
            "prefix": prefix,
            "base_prefix": base,
            "stdlib": f"{base}/Lib",
            "python_version": "3.14.0",
            "is_venv": prefix != base,
            "user_site": "C:/Users/fixture/AppData/Roaming/Python/site-packages",
            "user_site_enabled": True,
            "externally_managed": externally_managed,
        }
        self.packages.setdefault(interpreter, {})
        self.inherited_packages.setdefault(interpreter, {})

    def add_package(
        self,
        interpreter: str,
        name: str,
        version: str,
        *,
        requested: bool,
        direct_url: object | None = None,
    ) -> None:
        interpreter = self._interpreter_key(interpreter)
        self.packages[interpreter][normalize_python_distribution_name(name)] = {
            "name": name,
            "version": version,
            "requested": requested,
            "direct_url": direct_url,
        }

    def add_inherited_package(
        self,
        interpreter: str,
        name: str,
        version: str,
    ) -> None:
        interpreter = self._interpreter_key(interpreter)
        self.inherited_packages[interpreter][
            normalize_python_distribution_name(name)
        ] = version

    @staticmethod
    def _specifier_name(specifier: str) -> str:
        return normalize_python_distribution_name(
            specifier.split("@", 1)[0]
            .split("=", 1)[0]
            .split("<", 1)[0]
            .split(">", 1)[0]
            .split("[", 1)[0]
            .strip()
        )

    @staticmethod
    def _specifier_version(specifier: str) -> str | None:
        if "==" not in specifier:
            return None
        return specifier.split("==", 1)[1].strip()

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        interpreter = self._interpreter_key(argv[0])
        if argv[1] == "-c":
            return ProcessResult(0, json.dumps(self.probes[interpreter]), "")

        self.assert_pip_shape(argv)
        args = argv[3:]
        if args == ["--version"]:
            return ProcessResult(0, "pip 26.2 from fixture", "")

        if args[:2] == ["inspect", "--local"]:
            installed = []
            for package in self.packages[interpreter].values():
                row = {
                    "metadata": {
                        "name": package["name"],
                        "version": package["version"],
                    },
                    "metadata_location": f"{self.probes[interpreter]['prefix']}/site-packages/{package['name']}.dist-info",
                    "installer": "pip",
                    "requested": package["requested"],
                }
                if package["direct_url"] is not None:
                    row["direct_url"] = package["direct_url"]
                installed.append(row)
            return ProcessResult(
                0,
                json.dumps(
                    {
                        "version": "1",
                        "pip_version": "26.2",
                        "installed": installed,
                        "environment": {},
                    }
                ),
                "",
            )

        if args and args[0] == "install" and "--dry-run" in args:
            specifier = args[-1]
            name = self._specifier_name(specifier)
            installed = self.packages[interpreter].get(name)
            inherited = self.inherited_packages[interpreter].get(name)
            exact = self._specifier_version(specifier)
            installed_version = (
                installed["version"] if installed is not None else inherited
            )
            satisfied = installed_version is not None and (
                exact is None or installed_version == exact
            )
            report_install = [] if satisfied else [
                {
                    "metadata": {
                        "name": name,
                        "version": exact or "latest",
                    },
                    "requested": True,
                }
            ]
            return ProcessResult(
                0,
                json.dumps(
                    {
                        "version": "1",
                        "pip_version": "26.2",
                        "install": report_install,
                        "environment": {},
                    }
                ),
                "",
            )

        if args and args[0] == "install":
            if self.native_failure:
                return ProcessResult(
                    1,
                    "",
                    "error: Microsoft Visual C++ 14.0 or greater is required",
                )
            specifier = args[-1]
            name = self._specifier_name(specifier)
            version = self._specifier_version(specifier) or "1.0"
            self.add_package(interpreter, name, version, requested=True)
            return ProcessResult(0, "installed", "")

        if args and args[0] == "uninstall":
            name = normalize_python_distribution_name(args[-1])
            self.packages[interpreter].pop(name, None)
            return ProcessResult(0, "uninstalled", "")

        return ProcessResult(99, "", f"unexpected fake command: {argv!r}")

    @staticmethod
    def assert_pip_shape(argv: list[str]) -> None:
        if argv[1:3] != ["-m", "pip"]:
            raise AssertionError(f"pip was not invoked through exact interpreter: {argv!r}")


class PipPackageBackendTests(unittest.TestCase):
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
    def runtime(interpreter: str, key: str = "3.14") -> RuntimeInstance:
        return RuntimeInstance(
            subject="python",
            version="3.14.0",
            backend="python-install-manager",
            backend_key=key,
            architecture="x64",
            distribution="PythonCore",
            executable=Path(interpreter),
            prefix=Path(interpreter).parent,
        )

    def test_name_normalization_and_desired_root_preserve_native_specifier(self):
        root = pip_desired_root("Some_Package>=2")
        self.assertEqual("some-package", root.backend_key)
        self.assertEqual("Some_Package>=2", root.native_specifier)

    def test_bare_url_requires_explicit_distribution_name(self):
        with self.assertRaises(ValueError):
            pip_desired_root("https://example.invalid/tool.whl")

        root = pip_desired_root(
            "https://example.invalid/tool.whl",
            name="remote-tool",
        )
        self.assertEqual("remote-tool", root.backend_key)

    def test_exact_interpreter_inventory_excludes_inherited_visibility(self):
        runner = FakePipRunner()
        interpreter = "C:/venv/Scripts/python.exe"
        runner.add_environment(
            interpreter,
            prefix="C:/venv",
            base_prefix="C:/Python314",
        )
        runner.add_package(interpreter, "local-root", "1", requested=True)
        runner.add_package(interpreter, "local-dep", "1", requested=False)
        backend = PipPackageEnvironmentBackend(
            [PipEnvironmentTarget(Path(interpreter), self.runtime(interpreter))],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            inventory = backend.discover_inventory(context, environment)

        self.assertEqual("venv", environment.identity.classification)
        self.assertEqual(
            {"local-root", "local-dep"},
            {item.normalized_name for item in inventory.packages},
        )
        kinds = {item.normalized_name: item.kind.value for item in inventory.packages}
        self.assertEqual("top_level", kinds["local-root"])
        self.assertEqual("transitive", kinds["local-dep"])
        self.assertTrue(
            any(call[1:5] == ["-m", "pip", "inspect", "--local"] for call in runner.calls)
        )

    def test_external_and_project_environments_cannot_be_adopted(self):
        runner = FakePipRunner()
        external = "C:/Python/System/python.exe"
        project = "C:/repo/.venv/Scripts/python.exe"
        runner.add_environment(external, prefix="C:/Python/System", externally_managed=True)
        runner.add_environment(
            project,
            prefix="C:/repo/.venv",
            base_prefix="C:/Python314",
        )
        backend = PipPackageEnvironmentBackend(
            [
                PipEnvironmentTarget(Path(external), self.runtime(external, "system")),
                PipEnvironmentTarget(
                    Path(project),
                    self.runtime(project, "project-base"),
                    project_owned=True,
                ),
            ],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environments = backend.discover_environments(context)
            external_env = next(
                item for item in environments if "externally-managed" in item.identity.classification
            )
            project_env = next(
                item for item in environments if item.identity.classification == "project-venv"
            )
            external_result = adopt_package_environment(
                context,
                backend,
                external_env.identity.backend_key,
            )
            project_result = adopt_package_environment(
                context,
                backend,
                project_env.identity.backend_key,
            )

        self.assertEqual(
            PackageEnvironmentOwnershipKind.EXTERNALLY_MANAGED_READ_ONLY,
            external_env.ownership,
        )
        self.assertEqual(
            PackageEnvironmentOwnershipKind.PROJECT_OWNED,
            project_env.ownership,
        )
        self.assertEqual("package_environment_not_adoptable", external_result.code)
        self.assertEqual("package_environment_not_adoptable", project_result.code)

    def test_reconcile_preserves_unknown_roots_and_tracks_exact_runtime(self):
        runner = FakePipRunner()
        interpreter = "C:/Python314/python.exe"
        runner.add_environment(interpreter, prefix="C:/Python314")
        runner.add_package(interpreter, "human-tool", "7", requested=True)
        runtime = self.runtime(interpreter)
        backend = PipPackageEnvironmentBackend(
            [PipEnvironmentTarget(Path(interpreter), runtime)],
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
            desired_root = pip_desired_root("managed-tool==2")
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (desired_root,),
            )
            reconciled = reconcile_package_environment(context, backend, desired)
            guard = package_environment_runtime_removal_guard(
                context,
                runtime,
                scope_subject="user:fixture",
            )

        self.assertEqual("package_environment_owned", adopted.code)
        self.assertEqual("package_environment_reconciled", reconciled.code)
        package_state = runner.packages[runner._interpreter_key(interpreter)]
        self.assertIn("human-tool", package_state)
        self.assertEqual("2", package_state["managed-tool"]["version"])
        self.assertEqual("runtime_has_owned_package_environments", guard.code)
        install_calls = [
            call
            for call in runner.calls
            if call[1:4] == ["-m", "pip", "install"]
            and "--dry-run" not in call
        ]
        self.assertEqual(1, len(install_calls))
        self.assertEqual(interpreter, install_calls[0][0])

    def test_persisted_root_provenance_avoids_re_resolving_same_specifier(self):
        runner = FakePipRunner()
        interpreter = "C:/Python314/python.exe"
        runner.add_environment(interpreter, prefix="C:/Python314")
        runtime = self.runtime(interpreter)
        target = PipEnvironmentTarget(Path(interpreter), runtime)

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            first = PipPackageEnvironmentBackend([target], runner=runner)
            environment = first.discover_environments(context)[0]
            adopt_package_environment(context, first, environment.identity.backend_key)
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (pip_desired_root("demo==1"),),
            )
            first_result = reconcile_package_environment(context, first, desired)
            self.assertEqual("package_environment_reconciled", first_result.code)

            runner.calls.clear()
            recovered = PipPackageEnvironmentBackend([target], runner=runner)
            second_result = reconcile_package_environment(context, recovered, desired)

        self.assertEqual("package_environment_reconciled", second_result.code)
        dry_runs = [
            call
            for call in runner.calls
            if call[1:4] == ["-m", "pip", "install"] and "--dry-run" in call
        ]
        self.assertEqual([], dry_runs)

    def test_direct_url_metadata_is_redacted_before_inventory_persistence(self):
        runner = FakePipRunner()
        interpreter = "C:/Python314/python.exe"
        runner.add_environment(interpreter, prefix="C:/Python314")
        runner.add_package(
            interpreter,
            "private-tool",
            "1",
            requested=True,
            direct_url={"url": "https://alice:secret@example.invalid/tool.whl?token=abc"},
        )
        backend = PipPackageEnvironmentBackend(
            [PipEnvironmentTarget(Path(interpreter), self.runtime(interpreter))],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            inventory = backend.discover_inventory(context, environment)

        metadata = inventory.packages[0].metadata
        self.assertNotIn("secret", json.dumps(dict(metadata)))
        self.assertNotIn("token=abc", json.dumps(dict(metadata)))
        self.assertIn("<redacted>", json.dumps(dict(metadata)))

    def test_inherited_distribution_is_installed_locally_when_desired(self):
        runner = FakePipRunner()
        interpreter = "C:/venv/Scripts/python.exe"
        runner.add_environment(
            interpreter,
            prefix="C:/venv",
            base_prefix="C:/Python314",
        )
        runner.add_inherited_package(interpreter, "shared-tool", "1")
        runtime = self.runtime(interpreter)
        backend = PipPackageEnvironmentBackend(
            [PipEnvironmentTarget(Path(interpreter), runtime)],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            adopt_package_environment(context, backend, environment.identity.backend_key)
            desired = PackageEnvironmentDesiredState(
                environment.identity,
                (pip_desired_root("shared-tool==1"),),
            )
            result = reconcile_package_environment(context, backend, desired)

        self.assertEqual("package_environment_reconciled", result.code)
        local = runner.packages[runner._interpreter_key(interpreter)]
        self.assertIn("shared-tool", local)
        installs = [
            call
            for call in runner.calls
            if call[1:4] == ["-m", "pip", "install"]
            and "--dry-run" not in call
        ]
        self.assertEqual(1, len(installs))
        self.assertIn("--ignore-installed", installs[0])

    def test_native_build_failure_is_explicit_and_does_not_annex_toolchain(self):
        runner = FakePipRunner()
        interpreter = "C:/Python314/python.exe"
        runner.add_environment(interpreter, prefix="C:/Python314")
        runner.native_failure = True
        backend = PipPackageEnvironmentBackend(
            [PipEnvironmentTarget(Path(interpreter), self.runtime(interpreter))],
            runner=runner,
        )

        with tempfile.TemporaryDirectory() as temp:
            context = self.context(Path(temp))
            environment = backend.discover_environments(context)[0]
            result = backend.install(
                context,
                environment,
                pip_desired_root("native-demo==1"),
            )

        self.assertEqual("pip_native_build_prerequisite_missing", result.code)
        self.assertEqual(1, result.data["exit_code"])


if __name__ == "__main__":
    unittest.main()
