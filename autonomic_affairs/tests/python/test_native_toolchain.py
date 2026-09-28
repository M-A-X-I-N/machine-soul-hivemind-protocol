from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    NativeToolchainRequirement,
    OperationContext,
    Platform,
    TargetAccount,
)
from annexation_procedures.native_toolchain import (
    NativeToolchainDiscoveryError,
    adopt_visual_studio_instance,
    check_native_toolchain_requirement,
    discover_visual_studio_instances,
    read_native_toolchain_ownership,
    reconcile_visual_studio_components,
)
from annexation_procedures.process import ProcessResult


X64_LATEST = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"
X64_PINNED = "Microsoft.VisualStudio.Component.VC.14.50.18.0.x86.x64"
SDK_26100 = "Microsoft.VisualStudio.Component.Windows11SDK.26100"
EXTRA = "Microsoft.VisualStudio.Component.CMake.Windows"


class FakeVisualStudio:
    def __init__(self) -> None:
        self.instances = {
            "ide": {
                "instanceId": "ide",
                "installationPath": r"C:\VS\IDE",
                "installationVersion": "18.10.12345.1",
                "productId": "Microsoft.VisualStudio.Product.Community",
                "displayName": "Visual Studio Community 2026",
                "channelId": "VisualStudio.18.Stable",
                "isComplete": True,
                "isLaunchable": True,
                "isPrerelease": False,
                "packages": {X64_LATEST, SDK_26100, EXTRA},
                "msvc": {"14.51.12345"},
            },
            "build": {
                "instanceId": "build",
                "installationPath": r"C:\VS\BuildTools",
                "installationVersion": "18.10.12345.1",
                "productId": "Microsoft.VisualStudio.Product.BuildTools",
                "displayName": "Visual Studio Build Tools 2026",
                "channelId": "VisualStudio.18.Stable",
                "isComplete": True,
                "isLaunchable": False,
                "isPrerelease": False,
                "packages": {X64_LATEST, X64_PINNED, SDK_26100},
                "msvc": {"14.50.99999", "14.51.12345"},
            },
        }
        self.calls: list[list[str]] = []
        self.setup_returncode = 0
        self.mutate_on_failure = False

    def _json(self) -> str:
        payload = []
        for item in self.instances.values():
            payload.append(
                {
                    key: value
                    for key, value in item.items()
                    if key not in {"packages", "msvc"}
                }
                | {
                    "packages": [
                        {"id": component}
                        for component in sorted(item["packages"])
                    ]
                }
            )
        return json.dumps(payload)

    def versions(self, path: Path):
        for item in self.instances.values():
            if Path(item["installationPath"]) == path:
                return tuple(sorted(item["msvc"]))
        return ()

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        if argv[0] == "vswhere.exe":
            return ProcessResult(0, self._json(), "")
        if argv[0] != "setup.exe":
            return ProcessResult(999, "", "unexpected executable")

        target_path = argv[argv.index("--installPath") + 1]
        target = next(
            item for item in self.instances.values()
            if item["installationPath"] == target_path
        )
        should_mutate = self.setup_returncode in {0, 1641, 3010} or self.mutate_on_failure
        if should_mutate:
            index = 0
            while index < len(argv):
                if argv[index] == "--add":
                    target["packages"].add(argv[index + 1])
                    index += 2
                    continue
                if argv[index] == "--remove":
                    target["packages"].discard(argv[index + 1])
                    index += 2
                    continue
                index += 1
        return ProcessResult(self.setup_returncode, "", "fixture failure" if self.setup_returncode else "")


class NativeToolchainTests(unittest.TestCase):
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

    def _discover(self, fake: FakeVisualStudio):
        return discover_visual_studio_instances(
            runner=fake,
            vswhere_path="vswhere.exe",
            version_lister=fake.versions,
        )

    def test_discovery_includes_build_tools_and_exact_components(self) -> None:
        fake = FakeVisualStudio()

        instances = self._discover(fake)

        self.assertEqual(["build", "ide"], [item.instance_id for item in instances])
        build = instances[0]
        self.assertEqual("Microsoft.VisualStudio.Product.BuildTools", build.product_id)
        self.assertFalse(build.is_launchable)
        self.assertTrue(build.is_complete)
        self.assertEqual({X64_LATEST, X64_PINNED, SDK_26100}, set(build.component_ids))
        self.assertEqual(("14.50.99999", "14.51.12345"), build.msvc_versions)
        self.assertEqual(
            [
                "vswhere.exe",
                "-all",
                "-products",
                "*",
                "-format",
                "json",
                "-utf8",
                "-include",
                "packages",
            ],
            fake.calls[0],
        )

    def test_discovery_rejects_duplicate_instance_identity(self) -> None:
        def duplicate_runner(argv):
            entry = {
                "instanceId": "same",
                "installationPath": r"C:\VS\One",
                "installationVersion": "18.10",
                "isComplete": True,
                "packages": [],
            }
            return ProcessResult(0, json.dumps([entry, entry]), "")

        with self.assertRaises(NativeToolchainDiscoveryError):
            discover_visual_studio_instances(
                runner=duplicate_runner,
                vswhere_path="vswhere.exe",
                version_lister=lambda path: (),
            )

    def test_prerequisite_query_accepts_nonlaunchable_build_tools(self) -> None:
        fake = FakeVisualStudio()
        requirement = NativeToolchainRequirement(
            required_components=frozenset({X64_PINNED}),
            windows_sdk_component=SDK_26100,
            msvc_version_prefix="14.50",
            host_architecture="x64",
            target_architecture="x64",
        )

        with tempfile.TemporaryDirectory() as raw:
            result = check_native_toolchain_requirement(
                self._context(Path(raw)),
                requirement,
                runner=fake,
                vswhere_path="vswhere.exe",
                version_lister=fake.versions,
            )

        self.assertEqual("native_toolchain_requirement_satisfied", result.code)
        self.assertEqual(
            ["build"],
            [item["instance_id"] for item in result.data["candidates"]],
        )

    def test_prerequisite_query_reports_missing_exact_pinned_component(self) -> None:
        fake = FakeVisualStudio()
        requirement = NativeToolchainRequirement(
            required_components=frozenset(
                {"Microsoft.VisualStudio.Component.VC.14.44.17.14.x86.x64"}
            ),
            target_architecture="amd64",
        )

        with tempfile.TemporaryDirectory() as raw:
            result = check_native_toolchain_requirement(
                self._context(Path(raw)),
                requirement,
                runner=fake,
                vswhere_path="vswhere.exe",
                version_lister=fake.versions,
            )

        self.assertEqual("native_toolchain_requirement_missing", result.code)

    def test_adoption_is_machine_host_scoped_not_target_account_scoped(self) -> None:
        fake = FakeVisualStudio()
        build = self._discover(fake)[0]

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = self._context(root, account="first")
            second = self._context(root, account="second")
            adopted = adopt_visual_studio_instance(first, build)

            self.assertEqual("visual_studio_instance_adopted", adopted.code)
            self.assertTrue(adopted.changed)
            observed = read_native_toolchain_ownership(second, "build")
            self.assertIsNotNone(observed)
            assert observed is not None
            self.assertEqual(build.installation_path, observed.installation_path)

    def test_adoption_does_not_claim_preexisting_components(self) -> None:
        fake = FakeVisualStudio()
        build = self._discover(fake)[0]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, build)
            state = read_native_toolchain_ownership(context, "build")

        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(frozenset(), state.owned_components)

    def test_reconcile_adds_only_missing_component_to_ownership(self) -> None:
        fake = FakeVisualStudio()
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, ide)
            result = reconcile_visual_studio_components(
                context,
                "ide",
                {X64_LATEST, SDK_26100, X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            state = read_native_toolchain_ownership(context, "ide")

        self.assertEqual("native_toolchain_components_reconciled", result.code)
        self.assertTrue(result.changed)
        self.assertEqual({X64_PINNED}, set(state.owned_components))
        self.assertIn(X64_LATEST, fake.instances["ide"]["packages"])
        self.assertIn(SDK_26100, fake.instances["ide"]["packages"])

    def test_reconcile_removes_owned_but_preserves_unowned_components(self) -> None:
        fake = FakeVisualStudio()
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, ide)
            reconcile_visual_studio_components(
                context,
                "ide",
                {X64_LATEST, X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            result = reconcile_visual_studio_components(
                context,
                "ide",
                set(),
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            state = read_native_toolchain_ownership(context, "ide")

        self.assertEqual("native_toolchain_components_reconciled", result.code)
        self.assertNotIn(X64_PINNED, fake.instances["ide"]["packages"])
        self.assertIn(X64_LATEST, fake.instances["ide"]["packages"])
        self.assertIn(SDK_26100, fake.instances["ide"]["packages"])
        self.assertIn(EXTRA, fake.instances["ide"]["packages"])
        self.assertEqual(frozenset(), state.owned_components)

    def test_reconcile_refuses_unadopted_instance(self) -> None:
        fake = FakeVisualStudio()

        with tempfile.TemporaryDirectory() as raw:
            result = reconcile_visual_studio_components(
                self._context(Path(raw)),
                "build",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )

        self.assertEqual("visual_studio_instance_not_adopted", result.code)
        self.assertFalse(any(call[0] == "setup.exe" for call in fake.calls))

    def test_reconcile_refuses_identity_path_change(self) -> None:
        fake = FakeVisualStudio()
        build = self._discover(fake)[0]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, build)
            fake.instances["build"]["installationPath"] = r"D:\Moved\BuildTools"
            result = reconcile_visual_studio_components(
                context,
                "build",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )

        self.assertEqual("visual_studio_instance_identity_mismatch", result.code)

    def test_incomplete_instance_is_not_mutated(self) -> None:
        fake = FakeVisualStudio()
        fake.instances["build"]["isComplete"] = False
        build = self._discover(fake)[0]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopted = adopt_visual_studio_instance(context, build)

        self.assertEqual("visual_studio_instance_incomplete", adopted.code)

    def test_dry_run_plans_exact_components_without_mutation_or_ownership(self) -> None:
        fake = FakeVisualStudio()
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            real = self._context(root)
            adopt_visual_studio_instance(real, ide)
            dry = self._context(root, dry_run=True)
            result = reconcile_visual_studio_components(
                dry,
                "ide",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            state = read_native_toolchain_ownership(real, "ide")

        self.assertEqual("would_reconcile_native_toolchain_components", result.code)
        self.assertEqual([X64_PINNED], result.data["add_components"])
        self.assertFalse(any(call[0] == "setup.exe" for call in fake.calls))
        self.assertEqual(frozenset(), state.owned_components)

    def test_restart_required_is_successful_and_recorded(self) -> None:
        fake = FakeVisualStudio()
        fake.setup_returncode = 3010
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, ide)
            result = reconcile_visual_studio_components(
                context,
                "ide",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )

        self.assertEqual("native_toolchain_components_reconciled", result.code)
        self.assertTrue(result.data["restart_required"])

    def test_elevation_failure_is_explicit_and_does_not_claim_uninstalled_component(self) -> None:
        fake = FakeVisualStudio()
        fake.setup_returncode = 740
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, ide)
            result = reconcile_visual_studio_components(
                context,
                "ide",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            state = read_native_toolchain_ownership(context, "ide")

        self.assertEqual("visual_studio_elevation_required", result.code)
        self.assertFalse(result.changed)
        self.assertEqual(frozenset(), state.owned_components)

    def test_failure_after_partial_add_records_observed_new_ownership(self) -> None:
        fake = FakeVisualStudio()
        fake.setup_returncode = 5003
        fake.mutate_on_failure = True
        ide = self._discover(fake)[1]

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            adopt_visual_studio_instance(context, ide)
            result = reconcile_visual_studio_components(
                context,
                "ide",
                {X64_PINNED},
                runner=fake,
                vswhere_path="vswhere.exe",
                setup_path="setup.exe",
                version_lister=fake.versions,
            )
            state = read_native_toolchain_ownership(context, "ide")

        self.assertEqual("visual_studio_installer_failed", result.code)
        self.assertTrue(result.changed)
        self.assertEqual({X64_PINNED}, set(state.owned_components))


if __name__ == "__main__":
    unittest.main()
