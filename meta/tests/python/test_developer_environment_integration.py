from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation.applications import discover_applications
from annexation.model import (
    DesiredPackageRoot,
    Operation,
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
    RuntimeDesiredState,
    RuntimeInstance,
    RuntimeInstanceRef,
    RuntimeSpec,
    Support,
    TargetAccount,
)
from annexation.package_environment import (
    adopt_package_environment,
    package_environment_runtime_removal_guard,
    read_package_environment_ownerships,
    reconcile_package_environment,
)
from annexation.runtime import reconcile_runtime


class IntegrationRuntimeBackend:
    def __init__(self, subject: str, name: str) -> None:
        self.subject = subject
        self.name = name
        self.instances: dict[str, RuntimeInstance] = {}
        self.selected: str | None = None
        self.calls: list[tuple[str, str]] = []

    def ownership_scope(self, context: OperationContext) -> str:
        return f"user:{context.target_account.name.casefold()}"

    def spec(self, version: str) -> RuntimeSpec:
        return RuntimeSpec(
            subject=self.subject,
            version=version,
            backend=self.name,
            backend_key=version,
            architecture="x64",
            distribution=f"{self.subject}-fixture",
        )

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        return tuple(self.instances.values())

    def selected_key(self, context: OperationContext) -> str | None:
        return self.selected

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        self.calls.append(("install", spec.backend_key))
        instance = RuntimeInstance(
            subject=self.subject,
            version=spec.version,
            backend=self.name,
            backend_key=spec.backend_key,
            architecture=spec.architecture,
            distribution=spec.distribution,
            executable=Path(f"C:/{self.subject}/{spec.backend_key}/runtime.exe"),
            prefix=Path(f"C:/{self.subject}/{spec.backend_key}"),
        )
        self.instances[spec.backend_key] = instance
        return OperationResult.success(
            "integration_runtime_installed",
            "runtime installed",
            changed=True,
        )

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        self.calls.append(("uninstall", instance.backend_key))
        self.instances.pop(instance.backend_key, None)
        if self.selected == instance.backend_key:
            self.selected = None
        return OperationResult.success(
            "integration_runtime_uninstalled",
            "runtime uninstalled",
            changed=True,
        )

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        self.calls.append(("select", instance.backend_key))
        self.selected = instance.backend_key
        return OperationResult.success(
            "integration_runtime_selected",
            "runtime selected",
            changed=True,
        )


class IntegrationPackageBackend:
    manager = "integration-pkg"
    name = "integration-runtime-bound"

    def __init__(
        self,
        runtime: RuntimeInstance,
        *,
        baseline_ownership: PackageEnvironmentOwnershipKind = (
            PackageEnvironmentOwnershipKind.UNMANAGED
        ),
    ) -> None:
        self.runtime = runtime
        self.baseline_ownership = baseline_ownership
        self.packages: dict[str, ObservedPackage] = {
            "pkg:human-tool": ObservedPackage(
                "pkg:human-tool",
                "human-tool",
                "9",
                PackageObservationKind.TOP_LEVEL,
                normalized_name="human-tool",
            )
        }
        self.calls: list[tuple[str, str]] = []

    def ownership_scope(self, context: OperationContext) -> str:
        return f"user:{context.target_account.name.casefold()}"

    def identity(self) -> PackageEnvironmentIdentity:
        return PackageEnvironmentIdentity(
            manager=self.manager,
            backend=self.name,
            backend_key=f"{self.runtime.backend}:{self.runtime.backend_key}|global",
            locator=PackageEnvironmentLocator(
                "integration-runtime-prefix",
                {"prefix": str(self.runtime.prefix)},
            ),
            classification="runtime-global-fixture",
            runtime=RuntimeInstanceRef.from_instance(
                self.runtime,
                scope_subject="user:fixture",
            ),
        )

    def discover_environments(
        self,
        context: OperationContext,
    ) -> tuple[PackageEnvironment, ...]:
        return (
            PackageEnvironment(
                self.identity(),
                ownership=self.baseline_ownership,
                mutation_policy=PackageMutationPolicy.READ_ONLY,
            ),
        )

    def check_tool(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> OperationResult:
        return OperationResult.success(
            "integration_package_tool_available",
            "package tool available",
        )

    def discover_inventory(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PackageInventory:
        return PackageInventory(
            environment.identity.backend_key,
            tuple(self.packages.values()),
        )

    def verify(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        desired_roots,
        inventory: PackageInventory,
        owned_roots,
    ) -> PackageVerification:
        roots: list[PackageRootResolution] = []
        for desired in desired_roots:
            package = self.packages.get(f"pkg:{desired.backend_key}")
            if package is None:
                roots.append(
                    PackageRootResolution(
                        desired.backend_key,
                        PackageRootStatus.MISSING,
                    )
                )
            else:
                roots.append(
                    PackageRootResolution(
                        desired.backend_key,
                        PackageRootStatus.SATISFIED,
                        observed_key=package.backend_key,
                        removal_key=package.backend_key,
                    )
                )
        return PackageVerification(environment.identity.backend_key, tuple(roots))

    def install(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        self.calls.append(("install", root.backend_key))
        self.packages[f"pkg:{root.backend_key}"] = ObservedPackage(
            f"pkg:{root.backend_key}",
            root.normalized_name or root.backend_key,
            "1",
            PackageObservationKind.TOP_LEVEL,
            normalized_name=root.normalized_name,
        )
        return OperationResult.success(
            "integration_package_installed",
            "package installed",
            changed=True,
        )

    def update(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        return OperationResult.success(
            "integration_package_updated",
            "package updated",
        )

    def remove(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        target,
    ) -> OperationResult:
        self.calls.append(("remove", target.removal_key))
        self.packages.pop(target.removal_key, None)
        return OperationResult.success(
            "integration_package_removed",
            "package removed",
            changed=True,
        )


class DeveloperEnvironmentIntegrationTests(unittest.TestCase):
    def context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount("fixture", root / "fixture", True),
        )

    @staticmethod
    def desired(
        backend: IntegrationRuntimeBackend,
        versions: tuple[str, ...],
        selected: str,
    ) -> RuntimeDesiredState:
        return RuntimeDesiredState(
            subject=backend.subject,
            backend=backend.name,
            instances=tuple(backend.spec(version) for version in versions),
            selected_key=selected,
        )

    def test_editor_declarations_remain_install_only(self) -> None:
        root = Path(__file__).resolve().parents[3]
        applications = {item.id: item for item in discover_applications(root)}

        for app_id in ("visual_studio_code", "jetbrains_toolbox"):
            declaration = applications[app_id].for_platform(Platform.WINDOWS)
            assert declaration is not None
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.INSTALL),
            )
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.UNINSTALL),
            )
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.CHECK_INSTALLED),
            )
            self.assertEqual(
                Support.UNSUPPORTED,
                declaration.support_for(Operation.APPLY_CONFIG),
            )
            self.assertEqual(
                Support.UNSUPPORTED,
                declaration.support_for(Operation.UNAPPLY_CONFIG),
            )
            self.assertEqual(
                Support.UNSUPPORTED,
                declaration.support_for(Operation.CHECK_CONFIG),
            )
            self.assertEqual((), declaration.configurations)

    def test_runtime_package_lifecycle_is_exact_and_default_independent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self.context(root)
            python = IntegrationRuntimeBackend("python", "python-fixture")
            node = IntegrationRuntimeBackend("node", "node-fixture")
            lua = IntegrationRuntimeBackend("lua", "lua-fixture")

            python_result = reconcile_runtime(
                context,
                python,
                self.desired(python, ("3.13", "3.14"), "3.14"),
            )
            node_result = reconcile_runtime(
                context,
                node,
                self.desired(node, ("22", "24"), "24"),
            )
            lua_result = reconcile_runtime(
                context,
                lua,
                self.desired(lua, ("5.1", "5.4"), "5.4"),
            )

            self.assertEqual("runtime_reconciled", python_result.code)
            self.assertEqual("runtime_reconciled", node_result.code)
            self.assertEqual("runtime_reconciled", lua_result.code)
            self.assertEqual({"3.13", "3.14"}, set(python.instances))
            self.assertEqual({"22", "24"}, set(node.instances))
            self.assertEqual({"5.1", "5.4"}, set(lua.instances))

            package_backend = IntegrationPackageBackend(node.instances["22"])
            environment = package_backend.discover_environments(context)[0]
            adopted = adopt_package_environment(
                context,
                package_backend,
                environment.identity.backend_key,
            )
            desired_package = PackageEnvironmentDesiredState(
                environment.identity,
                (
                    DesiredPackageRoot(
                        "managed-cli",
                        "managed-cli@1",
                        "managed-cli",
                    ),
                ),
            )
            packages = reconcile_package_environment(
                context,
                package_backend,
                desired_package,
            )
            ownership_before = read_package_environment_ownerships(context)

            package_backend.calls.clear()
            node.calls.clear()
            switched = reconcile_runtime(
                context,
                node,
                self.desired(node, ("22", "24"), "22"),
            )
            switched_back = reconcile_runtime(
                context,
                node,
                self.desired(node, ("22", "24"), "24"),
            )
            ownership_after = read_package_environment_ownerships(context)

            removal_attempt = reconcile_runtime(
                context,
                node,
                self.desired(node, ("24",), "24"),
                removal_guard=package_environment_runtime_removal_guard,
            )

        self.assertEqual("package_environment_owned", adopted.code)
        self.assertEqual("package_environment_reconciled", packages.code)
        self.assertIn("pkg:human-tool", package_backend.packages)
        self.assertIn("pkg:managed-cli", package_backend.packages)
        self.assertEqual("runtime_reconciled", switched.code)
        self.assertEqual("runtime_reconciled", switched_back.code)
        self.assertEqual([], package_backend.calls)
        self.assertEqual(ownership_before, ownership_after)
        self.assertEqual("runtime_removal_blocked", removal_attempt.code)
        self.assertIn("22", node.instances)
        self.assertEqual("24", node.selected)

    def test_backend_migration_project_and_secret_boundaries_remain_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self.context(root)
            first = IntegrationRuntimeBackend("python", "manager-a")
            second = IntegrationRuntimeBackend("python", "manager-b")

            first_result = reconcile_runtime(
                context,
                first,
                self.desired(first, ("3.14",), "3.14"),
            )
            migration = reconcile_runtime(
                context,
                second,
                self.desired(second, ("3.14",), "3.14"),
            )

            project_backend = IntegrationPackageBackend(
                first.instances["3.14"],
                baseline_ownership=PackageEnvironmentOwnershipKind.PROJECT_OWNED,
            )
            project_environment = project_backend.discover_environments(context)[0]
            project_adoption = adopt_package_environment(
                context,
                project_backend,
                project_environment.identity.backend_key,
            )

        self.assertEqual("runtime_reconciled", first_result.code)
        self.assertEqual("runtime_backend_migration_required", migration.code)
        self.assertEqual([], second.calls)
        self.assertEqual("package_environment_not_adoptable", project_adoption.code)

        with self.assertRaises(ValueError):
            DesiredPackageRoot(
                "private-tool",
                "private-tool @ https://user:password@example.invalid/tool.whl",
                "private-tool",
            )


if __name__ == "__main__":
    unittest.main()
