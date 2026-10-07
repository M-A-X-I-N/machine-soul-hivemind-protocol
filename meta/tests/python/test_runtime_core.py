from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation.model import (
    OperationContext,
    OperationResult,
    Platform,
    RuntimeDesiredState,
    RuntimeInstance,
    RuntimeSpec,
    TargetAccount,
)
from annexation.runtime import (
    RuntimeStateError,
    adopt_runtime_instance,
    read_runtime_ownerships,
    reconcile_runtime,
)


class FakeRuntimeBackend:
    def __init__(
        self,
        *,
        subject: str = "fixture",
        name: str = "fixture-manager",
        user_scoped: bool = False,
    ) -> None:
        self.subject = subject
        self.name = name
        self.instances: dict[str, RuntimeInstance] = {}
        self.unmanaged: list[RuntimeInstance] = []
        self.selected: str | None = None
        self.calls: list[tuple[str, str]] = []
        self.fail_install: set[str] = set()
        self.fail_uninstall: set[str] = set()
        self.fail_select: set[str] = set()
        self.user_scoped = user_scoped

    def ownership_scope(self, context: OperationContext) -> str | None:
        if not self.user_scoped:
            return None
        return f"user:{context.target_account.name.casefold()}"

    def spec(self, version: str, key: str | None = None) -> RuntimeSpec:
        return RuntimeSpec(
            subject=self.subject,
            version=version,
            backend=self.name,
            backend_key=key or version,
            architecture="x64",
            distribution="fixture-dist",
        )

    def instance(self, version: str, key: str | None = None) -> RuntimeInstance:
        actual_key = key or version
        return RuntimeInstance(
            subject=self.subject,
            version=version,
            backend=self.name,
            backend_key=actual_key,
            architecture="x64",
            distribution="fixture-dist",
            executable=Path(f"C:/fixture/{actual_key}/runtime.exe"),
            prefix=Path(f"C:/fixture/{actual_key}"),
        )

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        return tuple(self.instances.values()) + tuple(self.unmanaged)

    def selected_key(self, context: OperationContext) -> str | None:
        return self.selected

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        self.calls.append(("install", spec.backend_key))
        if spec.backend_key in self.fail_install:
            return OperationResult.error("fixture_install_failed", "fixture install failed")
        self.instances[spec.backend_key] = self.instance(spec.version, spec.backend_key)
        return OperationResult.success(
            "fixture_installed",
            "fixture installed",
            changed=True,
        )

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        self.calls.append(("uninstall", instance.backend_key))
        if instance.backend_key in self.fail_uninstall:
            return OperationResult.error("fixture_uninstall_failed", "fixture uninstall failed")
        self.instances.pop(instance.backend_key, None)
        if self.selected == instance.backend_key:
            self.selected = None
        return OperationResult.success(
            "fixture_uninstalled",
            "fixture uninstalled",
            changed=True,
        )

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        self.calls.append(("select", instance.backend_key))
        if instance.backend_key in self.fail_select:
            return OperationResult.error("fixture_select_failed", "fixture select failed")
        self.selected = instance.backend_key
        return OperationResult.success(
            "fixture_selected",
            "fixture selected",
            changed=True,
        )


class DuplicateBackend(FakeRuntimeBackend):
    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        return (self.instance("1.0", "same"), self.instance("1.1", "same"))


class RuntimeCoreTests(unittest.TestCase):
    def _context(
        self,
        root: Path,
        *,
        account: str = "fixture",
        dry_run: bool = False,
    ) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount(account, root / account, True),
            dry_run=dry_run,
        )

    def _desired(
        self,
        backend: FakeRuntimeBackend,
        versions: tuple[str, ...],
        *,
        selected: str | None,
    ) -> RuntimeDesiredState:
        return RuntimeDesiredState(
            subject=backend.subject,
            backend=backend.name,
            instances=tuple(backend.spec(version) for version in versions),
            selected_key=selected,
        )

    def test_desired_state_accepts_deliberate_multiversion_set(self) -> None:
        backend = FakeRuntimeBackend()

        desired = self._desired(backend, ("1.0", "2.0", "3.0"), selected="2.0")

        self.assertEqual({"1.0", "2.0", "3.0"}, set(desired.desired_keys))
        self.assertEqual("2.0", desired.selected_key)

    def test_desired_state_rejects_selected_runtime_outside_set(self) -> None:
        backend = FakeRuntimeBackend()

        with self.assertRaises(ValueError):
            self._desired(backend, ("1.0",), selected="2.0")

    def test_multiversion_reconcile_installs_all_and_selects_one(self) -> None:
        backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0"), selected="2.0"),
            )
            states = read_runtime_ownerships(context, backend.subject)

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual({"1.0", "2.0"}, set(backend.instances))
        self.assertEqual("2.0", backend.selected)
        self.assertEqual(
            {("install", "1.0"), ("install", "2.0"), ("select", "2.0")},
            set(backend.calls),
        )
        self.assertEqual({"1.0", "2.0"}, {state.backend_key for state in states})

    def test_default_only_change_does_not_reinstall(self) -> None:
        backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0"), selected="1.0"),
            )
            backend.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0"), selected="2.0"),
            )

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual([("select", "2.0")], backend.calls)
        self.assertEqual("2.0", backend.selected)

    def test_exact_removal_preserves_other_owned_versions(self) -> None:
        backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0", "3.0"), selected="2.0"),
            )
            backend.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("2.0", "3.0"), selected="2.0"),
            )
            states = read_runtime_ownerships(context, backend.subject)

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual([("uninstall", "1.0")], backend.calls)
        self.assertEqual({"2.0", "3.0"}, set(backend.instances))
        self.assertEqual({"2.0", "3.0"}, {state.backend_key for state in states})

    def test_selected_owned_removal_without_reselection_is_refused_before_mutation(self) -> None:
        backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0"), selected="1.0"),
            )
            backend.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("2.0",), selected=None),
            )

        self.assertEqual("runtime_selected_removal_requires_reselection", result.code)
        self.assertEqual([], backend.calls)
        self.assertEqual({"1.0", "2.0"}, set(backend.instances))
        self.assertEqual("1.0", backend.selected)

    def test_selected_owned_removal_reselects_before_uninstall(self) -> None:
        backend = FakeRuntimeBackend()

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0", "2.0"), selected="1.0"),
            )
            backend.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("2.0",), selected="2.0"),
            )

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual([("select", "2.0"), ("uninstall", "1.0")], backend.calls)
        self.assertEqual("2.0", backend.selected)

    def test_preexisting_desired_instance_requires_explicit_adoption(self) -> None:
        backend = FakeRuntimeBackend()
        backend.instances["1.0"] = backend.instance("1.0")

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            refused = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0",), selected="1.0"),
            )
            adopted = adopt_runtime_instance(context, backend, "1.0")
            reconciled = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0",), selected="1.0"),
            )

        self.assertEqual("runtime_unmanaged_conflict", refused.code)
        self.assertEqual("runtime_instance_adopted", adopted.code)
        self.assertEqual("runtime_reconciled", reconciled.code)

    def test_unmanaged_other_backend_observation_does_not_become_owned(self) -> None:
        backend = FakeRuntimeBackend()
        backend.unmanaged.append(
            RuntimeInstance(
                subject=backend.subject,
                version="9.9",
                backend="legacy-installer",
                backend_key="legacy-9.9",
                executable=Path("C:/legacy/runtime.exe"),
            )
        )

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0",), selected="1.0"),
            )
            states = read_runtime_ownerships(context, backend.subject)

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual({"1.0"}, {state.backend_key for state in states})
        self.assertIn("legacy-9.9", {item.backend_key for item in backend.discover(context)})

    def test_duplicate_exact_backend_keys_are_ambiguous(self) -> None:
        backend = DuplicateBackend()

        with tempfile.TemporaryDirectory() as raw:
            result = reconcile_runtime(
                self._context(Path(raw)),
                backend,
                self._desired(backend, ("same",), selected="same"),
            )

        self.assertEqual("runtime_discovery_ambiguous", result.code)

    def test_backend_switch_requires_explicit_migration(self) -> None:
        first = FakeRuntimeBackend(name="manager-a")
        first.instances["1.0"] = first.instance("1.0")
        second = FakeRuntimeBackend(name="manager-b")

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopted = adopt_runtime_instance(context, first, "1.0")
            result = reconcile_runtime(
                context,
                second,
                self._desired(second, ("1.0",), selected="1.0"),
            )

        self.assertEqual("runtime_instance_adopted", adopted.code)
        self.assertEqual("runtime_backend_migration_required", result.code)
        self.assertEqual([], second.calls)

    def test_user_scoped_runtime_ownership_can_coexist_across_accounts(self) -> None:
        first_backend = FakeRuntimeBackend(user_scoped=True)
        second_backend = FakeRuntimeBackend(user_scoped=True)
        first_backend.instances["1.0"] = first_backend.instance("1.0")
        second_backend.instances["1.0"] = second_backend.instance("1.0")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = self._context(root, account="First")
            second = self._context(root, account="Second")
            first_result = adopt_runtime_instance(first, first_backend, "1.0")
            second_result = adopt_runtime_instance(second, second_backend, "1.0")
            states = read_runtime_ownerships(first, first_backend.subject)

        self.assertEqual("runtime_instance_adopted", first_result.code)
        self.assertEqual("runtime_instance_adopted", second_result.code)
        self.assertEqual(
            {"user:first", "user:second"},
            {state.scope_subject for state in states},
        )

    def test_runtime_ownership_is_host_scoped_not_target_account_scoped(self) -> None:
        backend = FakeRuntimeBackend()
        backend.instances["1.0"] = backend.instance("1.0")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = self._context(root, account="first")
            second = self._context(root, account="second")
            adopt_runtime_instance(first, backend, "1.0")
            states = read_runtime_ownerships(second, backend.subject)

        self.assertEqual({"1.0"}, {state.backend_key for state in states})

    def test_dry_run_reports_set_selection_and_removal_without_mutation(self) -> None:
        backend = FakeRuntimeBackend()
        backend.instances["1.0"] = backend.instance("1.0")

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            real = self._context(root)
            adopt_runtime_instance(real, backend, "1.0")
            backend.selected = "1.0"
            dry = self._context(root, dry_run=True)
            result = reconcile_runtime(
                dry,
                backend,
                self._desired(backend, ("2.0",), selected="2.0"),
            )

        self.assertEqual("would_reconcile_runtime", result.code)
        self.assertEqual(["2.0"], result.data["install_keys"])
        self.assertEqual(["1.0"], result.data["remove_keys"])
        self.assertEqual("2.0", result.data["select_key"])
        self.assertEqual([], backend.calls)
        self.assertEqual({"1.0"}, set(backend.instances))

    def test_failed_install_does_not_create_ownership(self) -> None:
        backend = FakeRuntimeBackend()
        backend.fail_install.add("1.0")

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0",), selected="1.0"),
            )
            states = read_runtime_ownerships(context, backend.subject)

        self.assertEqual("runtime_install_failed", result.code)
        self.assertEqual((), states)

    def test_owned_instance_identity_drift_is_refused(self) -> None:
        backend = FakeRuntimeBackend()
        backend.instances["1.0"] = backend.instance("1.0")

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_runtime_instance(context, backend, "1.0")
            backend.instances["1.0"] = RuntimeInstance(
                subject=backend.subject,
                version="1.0",
                backend=backend.name,
                backend_key="1.0",
                architecture="arm64",
                distribution="fixture-dist",
                executable=Path("C:/different/runtime.exe"),
            )
            result = reconcile_runtime(
                context,
                backend,
                self._desired(backend, ("1.0",), selected="1.0"),
            )

        self.assertEqual("runtime_provenance_mismatch", result.code)


if __name__ == "__main__":
    unittest.main()
