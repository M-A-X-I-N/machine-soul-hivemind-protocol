from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    DesiredPackageRoot,
    OperationContext,
    OperationResult,
    PackageEnvironment,
    PackageEnvironmentDesiredState,
    PackageEnvironmentIdentity,
    PackageEnvironmentLocator,
    PackageEnvironmentOwnershipKind,
    PackageInventory,
    PackageMutationPolicy,
    PackageObservationKind,
    PackageRootResolution,
    PackageRootStatus,
    PackageVerification,
    ObservedPackage,
    Platform,
    RuntimeInstance,
    RuntimeInstanceRef,
    RuntimeDesiredState,
    RuntimeSpec,
    TargetAccount,
)
from annexation_procedures.package_environment import (
    adopt_package_environment,
    package_environment_runtime_removal_guard,
    read_package_environment_ownerships,
    reconcile_package_environment,
    register_created_package_environment,
)
from annexation_procedures.runtime import (
    adopt_runtime_instance,
    reconcile_runtime,
)


class FakePackageBackend:
    def __init__(
        self,
        *,
        manager: str,
        name: str,
        locator_kind: str,
        runtime: RuntimeInstance | None = None,
        runtime_scope: str | None = None,
        baseline_ownership: PackageEnvironmentOwnershipKind = PackageEnvironmentOwnershipKind.UNMANAGED,
    ) -> None:
        self.manager = manager
        self.name = name
        self.locator_kind = locator_kind
        self.runtime = runtime
        self.runtime_scope = runtime_scope
        self.baseline_ownership = baseline_ownership
        self.packages: dict[str, ObservedPackage] = {}
        self.desired_to_package: dict[str, str] = {}
        self.calls: list[tuple[str, str]] = []

    def ownership_scope(self, context: OperationContext) -> str | None:
        return f"user:{context.target_account.name.casefold()}"

    def identity(self, key: str = "env") -> PackageEnvironmentIdentity:
        runtime_ref = (
            RuntimeInstanceRef.from_instance(
                self.runtime,
                scope_subject=self.runtime_scope,
            )
            if self.runtime is not None
            else None
        )
        return PackageEnvironmentIdentity(
            manager=self.manager,
            backend=self.name,
            backend_key=key,
            locator=PackageEnvironmentLocator(
                self.locator_kind,
                {"location": f"C:/fixture/{self.name}/{key}"},
            ),
            classification=f"{self.locator_kind}-fixture",
            runtime=runtime_ref,
        )

    def environment(self, key: str = "env") -> PackageEnvironment:
        return PackageEnvironment(
            self.identity(key),
            ownership=self.baseline_ownership,
            mutation_policy=PackageMutationPolicy.READ_ONLY,
        )

    def discover_environments(self, context: OperationContext):
        return (self.environment(),)

    def check_tool(self, context: OperationContext, environment: PackageEnvironment):
        return OperationResult.success("fixture_tool_available", "fixture tool available")

    def discover_inventory(self, context: OperationContext, environment: PackageEnvironment):
        return PackageInventory(environment.identity.backend_key, tuple(self.packages.values()))

    def verify(self, context, environment, desired_roots, inventory, owned_roots):
        resolutions = []
        for root in desired_roots:
            package_key = self.desired_to_package.get(root.backend_key)
            package = self.packages.get(package_key) if package_key else None
            if package is None:
                status = PackageRootStatus.MISSING
                observed_key = None
                removal_key = None
            elif package.version == "old":
                status = PackageRootStatus.UPDATE_REQUIRED
                observed_key = package.backend_key
                removal_key = package.backend_key
            else:
                status = PackageRootStatus.SATISFIED
                observed_key = package.backend_key
                removal_key = package.backend_key
            resolutions.append(
                PackageRootResolution(
                    root.backend_key,
                    status,
                    observed_key=observed_key,
                    removal_key=removal_key,
                )
            )
        return PackageVerification(environment.identity.backend_key, tuple(resolutions))

    def install(self, context, environment, root):
        self.calls.append(("install", root.backend_key))
        package_key = f"pkg:{root.normalized_name or root.backend_key}"
        self.desired_to_package[root.backend_key] = package_key
        self.packages[package_key] = ObservedPackage(
            package_key,
            root.normalized_name or root.backend_key,
            "1",
            PackageObservationKind.TOP_LEVEL,
            normalized_name=root.normalized_name,
        )
        return OperationResult.success("fixture_package_installed", "installed", changed=True)

    def update(self, context, environment, root):
        self.calls.append(("update", root.backend_key))
        package_key = self.desired_to_package[root.backend_key]
        package = self.packages[package_key]
        self.packages[package_key] = ObservedPackage(
            package.backend_key,
            package.native_name,
            "2",
            package.kind,
            normalized_name=package.normalized_name,
        )
        return OperationResult.success("fixture_package_updated", "updated", changed=True)

    def remove(self, context, environment, target):
        self.calls.append(("remove", target.removal_key))
        self.packages.pop(target.removal_key, None)
        return OperationResult.success("fixture_package_removed", "removed", changed=True)


class FakeRuntimeBackend:
    subject = "python"
    name = "python-manager"

    def __init__(self) -> None:
        self.instances: dict[str, RuntimeInstance] = {}

    def ownership_scope(self, context):
        return f"user:{context.target_account.name.casefold()}"

    def discover(self, context):
        return tuple(self.instances.values())

    def selected_key(self, context):
        return None

    def install(self, context, spec):
        instance = RuntimeInstance(
            subject=self.subject,
            version=spec.version,
            backend=self.name,
            backend_key=spec.backend_key,
            architecture="x64",
            executable=Path(f"C:/python/{spec.backend_key}/python.exe"),
            prefix=Path(f"C:/python/{spec.backend_key}"),
        )
        self.instances[spec.backend_key] = instance
        return OperationResult.success("runtime_installed", "installed", changed=True)

    def uninstall(self, context, instance):
        self.instances.pop(instance.backend_key, None)
        return OperationResult.success("runtime_uninstalled", "uninstalled", changed=True)

    def select(self, context, instance):
        return OperationResult.success("runtime_selected", "selected")


class PackageEnvironmentCoreTests(unittest.TestCase):
    def context(self, root: Path, *, dry_run: bool = False):
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount("fixture", root / "fixture", True),
            dry_run=dry_run,
        )

    def desired(self, backend: FakePackageBackend, *roots: DesiredPackageRoot):
        return PackageEnvironmentDesiredState(backend.identity(), tuple(roots))

    def test_backend_specific_locators_allow_same_runtime_multiple_environments(self):
        runtime = RuntimeInstance("python", "3.14", "py", "3.14")
        tree = FakePackageBackend(manager="fixture", name="tree", locator_kind="tree", runtime=runtime)
        interpreter = FakePackageBackend(manager="fixture", name="interpreter", locator_kind="interpreter", runtime=runtime)
        prefix = FakePackageBackend(manager="fixture", name="prefix", locator_kind="prefix", runtime=runtime)

        identities = {tree.identity(), interpreter.identity(), prefix.identity()}

        self.assertEqual(3, len(identities))
        self.assertEqual({"tree", "interpreter", "prefix"}, {item.locator.kind for item in identities})

    def test_desired_roots_are_not_observed_transitive_packages(self):
        backend = FakePackageBackend(manager="fixture", name="tree", locator_kind="tree")
        root = DesiredPackageRoot("root", "root >= 1", "root")
        backend.desired_to_package["root"] = "pkg:root"
        backend.packages["pkg:root"] = ObservedPackage(
            "pkg:root", "root", "1", PackageObservationKind.TOP_LEVEL, normalized_name="root"
        )
        backend.packages["pkg:dependency"] = ObservedPackage(
            "pkg:dependency", "dependency", "4", PackageObservationKind.TRANSITIVE
        )

        inventory = backend.discover_inventory(self.context(Path(".")), backend.environment())
        desired = self.desired(backend, root)

        self.assertEqual({"root"}, set(desired.desired_keys))
        self.assertEqual(2, len(inventory.packages))
        self.assertEqual(
            PackageObservationKind.TRANSITIVE,
            next(item.kind for item in inventory.packages if item.backend_key == "pkg:dependency"),
        )

    def test_adopt_reconcile_preserves_unknown_top_level_and_owns_desired_root(self):
        backend = FakePackageBackend(manager="fixture", name="tree", locator_kind="tree")
        root = DesiredPackageRoot("root", "root >= 1", "root")
        backend.desired_to_package["root"] = "pkg:root"
        backend.packages["pkg:root"] = ObservedPackage(
            "pkg:root", "root", "1", PackageObservationKind.TOP_LEVEL, normalized_name="root"
        )
        backend.packages["pkg:unknown"] = ObservedPackage(
            "pkg:unknown", "unknown", "9", PackageObservationKind.TOP_LEVEL
        )

        with tempfile.TemporaryDirectory() as raw:
            context = self.context(Path(raw))
            adopted = adopt_package_environment(context, backend, "env")
            result = reconcile_package_environment(context, backend, self.desired(backend, root))
            ownership = read_package_environment_ownerships(context)[0]

        self.assertEqual("package_environment_owned", adopted.code)
        self.assertEqual("package_environment_reconciled", result.code)
        self.assertEqual([], backend.calls)
        self.assertIn("pkg:unknown", backend.packages)
        self.assertEqual(("root",), tuple(item.backend_key for item in ownership.roots))

    def test_removing_desired_root_only_removes_machine_soul_owned_root(self):
        backend = FakePackageBackend(manager="fixture", name="prefix", locator_kind="prefix")
        root = DesiredPackageRoot("root", "root@^1", "root")
        backend.desired_to_package["root"] = "pkg:root"
        backend.packages["pkg:root"] = ObservedPackage(
            "pkg:root", "root", "1", PackageObservationKind.TOP_LEVEL, normalized_name="root"
        )
        backend.packages["pkg:unknown"] = ObservedPackage(
            "pkg:unknown", "unknown", "3", PackageObservationKind.TOP_LEVEL
        )

        with tempfile.TemporaryDirectory() as raw:
            context = self.context(Path(raw))
            adopt_package_environment(context, backend, "env")
            reconcile_package_environment(context, backend, self.desired(backend, root))
            backend.calls.clear()
            result = reconcile_package_environment(context, backend, self.desired(backend))

        self.assertEqual("package_environment_reconciled", result.code)
        self.assertEqual([("remove", "pkg:root")], backend.calls)
        self.assertIn("pkg:unknown", backend.packages)

    def test_exclusive_policy_removes_unknown_top_level_but_not_transitives(self):
        backend = FakePackageBackend(manager="fixture", name="prefix", locator_kind="prefix")
        backend.packages["pkg:unknown"] = ObservedPackage(
            "pkg:unknown", "unknown", "1", PackageObservationKind.TOP_LEVEL
        )
        backend.packages["pkg:dependency"] = ObservedPackage(
            "pkg:dependency", "dependency", "1", PackageObservationKind.TRANSITIVE
        )

        with tempfile.TemporaryDirectory() as raw:
            context = self.context(Path(raw))
            adopt_package_environment(
                context,
                backend,
                "env",
                mutation_policy=PackageMutationPolicy.EXCLUSIVE,
            )
            result = reconcile_package_environment(context, backend, self.desired(backend))

        self.assertEqual("package_environment_reconciled", result.code)
        self.assertNotIn("pkg:unknown", backend.packages)
        self.assertIn("pkg:dependency", backend.packages)

    def test_project_external_and_ephemeral_environments_are_not_adopted(self):
        kinds = (
            PackageEnvironmentOwnershipKind.PROJECT_OWNED,
            PackageEnvironmentOwnershipKind.EXTERNALLY_MANAGED_READ_ONLY,
            PackageEnvironmentOwnershipKind.EPHEMERAL_UNMANAGED,
        )
        for kind in kinds:
            with self.subTest(kind=kind):
                backend = FakePackageBackend(
                    manager="fixture",
                    name=f"backend-{kind.value}",
                    locator_kind="interpreter",
                    baseline_ownership=kind,
                )
                with tempfile.TemporaryDirectory() as raw:
                    result = adopt_package_environment(self.context(Path(raw)), backend, "env")
                self.assertEqual("package_environment_not_adoptable", result.code)

    def test_read_only_owned_environment_refuses_required_mutation(self):
        backend = FakePackageBackend(manager="fixture", name="tree", locator_kind="tree")
        root = DesiredPackageRoot("root", "root", "root")

        with tempfile.TemporaryDirectory() as raw:
            context = self.context(Path(raw))
            adopt_package_environment(
                context,
                backend,
                "env",
                mutation_policy=PackageMutationPolicy.READ_ONLY,
            )
            result = reconcile_package_environment(context, backend, self.desired(backend, root))

        self.assertEqual("package_environment_read_only", result.code)
        self.assertEqual([], backend.calls)

    def test_backend_diagnostic_is_redacted_before_shared_result(self):
        class LeakyBackend(FakePackageBackend):
            def install(self, context, environment, root):
                return OperationResult.error(
                    "fixture_leak",
                    "failed https://alice:hunter2@example.test/simple",
                    data={"token": "supersecret", "url": "https://bob:pw@example.test"},
                )

        backend = LeakyBackend(manager="fixture", name="tree", locator_kind="tree")
        root = DesiredPackageRoot("root", "root", "root")

        with tempfile.TemporaryDirectory() as raw:
            context = self.context(Path(raw))
            adopt_package_environment(context, backend, "env")
            result = reconcile_package_environment(context, backend, self.desired(backend, root))

        backend_result = result.data["backend_result"]
        self.assertNotIn("hunter2", str(backend_result))
        self.assertNotIn("supersecret", str(backend_result))
        self.assertNotIn("bob:pw", str(backend_result))
        self.assertIn("<redacted>", str(backend_result))

    def test_persisted_desired_state_rejects_credential_bearing_specifier(self):
        with self.assertRaises(ValueError):
            DesiredPackageRoot(
                "private",
                "pkg @ https://user:password@example.test/pkg.whl",
                "pkg",
            )

    def test_runtime_removal_guard_blocks_owned_bound_environment(self):
        runtime_backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            root_path = Path(raw)
            context = self.context(root_path)
            spec = RuntimeSpec(
                "python", "3.14", runtime_backend.name, "3.14", architecture="x64"
            )
            runtime_backend.install(context, spec)
            runtime = runtime_backend.instances["3.14"]
            adopt_runtime_instance(context, runtime_backend, "3.14")

            package_backend = FakePackageBackend(
                manager="pip",
                name="pip-fixture",
                locator_kind="interpreter",
                runtime=runtime,
                runtime_scope="user:fixture",
            )
            register_created_package_environment(context, package_backend, "env")

            desired_runtime = RuntimeDesiredState(
                "python",
                runtime_backend.name,
                (),
                selected_key=None,
            )
            result = reconcile_runtime(
                context,
                runtime_backend,
                desired_runtime,
                removal_guard=package_environment_runtime_removal_guard,
            )

        self.assertEqual("runtime_removal_blocked", result.code)
        self.assertIn("3.14", runtime_backend.instances)

    def test_runtime_removal_guard_allows_unbound_runtime(self):
        runtime = RuntimeInstance(
            "python",
            "3.14",
            "python-manager",
            "3.14",
            architecture="x64",
        )
        with tempfile.TemporaryDirectory() as raw:
            result = package_environment_runtime_removal_guard(
                self.context(Path(raw)),
                runtime,
                "user:fixture",
            )
        self.assertEqual("runtime_package_environment_dependencies_clear", result.code)


if __name__ == "__main__":
    unittest.main()
