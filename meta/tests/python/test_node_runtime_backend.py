from __future__ import annotations

import json
import ntpath
from pathlib import Path
import tempfile
import unittest

from annexation.model import (
    OperationContext,
    Platform,
    RuntimeDesiredState,
    TargetAccount,
)
from annexation.node_runtime import (
    NvmWindowsV2Backend,
    NvmWindowsV2Error,
    nvm_windows_runtime_spec,
)
from annexation.process import ProcessResult
from annexation.runtime import read_runtime_ownerships, reconcile_runtime


class FakeNvmV2:
    def __init__(self) -> None:
        self.root = r"C:\Users\fixture\AppData\Local\Author Software\nvm"
        self.program_root = r"C:\Program Files\Author Software\nvm"
        self.versions: dict[str, str] = {}
        self.selected: str | None = None
        self.calls: list[list[str]] = []
        self.path_node: str | None = r"C:\Legacy\node.exe"
        self.path_node_version = "20.19.5"
        self.path_node_arch = "x64"

    def _node_version_for_path(self, executable: str) -> str | None:
        if self.path_node and ntpath.normcase(executable) == ntpath.normcase(self.path_node):
            return self.path_node_version
        normalized = ntpath.normpath(executable)
        for version in self.versions:
            expected = ntpath.normpath(
                ntpath.join(self.root, f"v{version}", "node.exe")
            )
            if ntpath.normcase(normalized) == ntpath.normcase(expected):
                return version
        return None

    def assert_config_call(self, argv: list[str]) -> None:
        expected = [
            ntpath.join(self.program_root, "nvm.exe"),
            "config",
            "get",
            "root",
            "mode",
            "--json",
        ]
        if argv != expected:
            raise AssertionError(f"unexpected config call: {argv!r}")

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        executable = argv[0]

        if ntpath.basename(executable).casefold() == "node.exe":
            version = self._node_version_for_path(executable)
            if version is None:
                return ProcessResult(91, "", "unknown node path")
            if argv[1:] == ["--version"]:
                return ProcessResult(0, f"v{version}\n", "")
            if argv[1:] == ["-p", "process.arch"]:
                arch = (
                    self.path_node_arch
                    if self.path_node
                    and ntpath.normcase(executable) == ntpath.normcase(self.path_node)
                    else "x64"
                )
                return ProcessResult(0, arch + "\n", "")
            return ProcessResult(92, "", "unexpected node probe")

        if ntpath.basename(executable).casefold() != "nvm.exe":
            return ProcessResult(90, "", "wrong executable")
        command = argv[1]
        if command == "config":
            self.assert_config_call(argv)
            return ProcessResult(
                0,
                json.dumps({"root": self.root, "mode": "shim"}),
                "",
            )
        if command == "list":
            rows = [
                {
                    "version": version,
                    "npm": npm,
                    "lts": version.startswith(("22.", "24.")),
                    "installed": True,
                    "cached": False,
                    "default": version == self.selected,
                }
                for version, npm in sorted(self.versions.items(), reverse=True)
            ]
            return ProcessResult(0, json.dumps(rows), "")
        if command == "default":
            return ProcessResult(
                0,
                json.dumps({"default": self.selected or "none"}),
                "",
            )
        if command == "install":
            version = argv[2].removeprefix("v")
            npm = {
                "22.20.0": "10.9.3",
                "24.9.0": "11.6.0",
                "26.0.0": "11.8.0",
            }.get(version, "11.0.0")
            self.versions[version] = npm
            return ProcessResult(0, "", "")
        if command == "uninstall":
            version = argv[2].removeprefix("v")
            self.versions.pop(version, None)
            if self.selected == version:
                self.selected = None
            return ProcessResult(0, "", "")
        if command == "use":
            version = argv[2].removeprefix("v")
            if version not in self.versions:
                return ProcessResult(1, "", "not installed")
            self.selected = version
            return ProcessResult(0, "", "")
        return ProcessResult(93, "", "unexpected nvm command")


class NvmWindowsV2BackendTests(unittest.TestCase):
    def _context(
        self,
        root: Path,
        *,
        account: str = "fixture",
        current: bool = True,
    ) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount(account, root / account, current),
        )

    def _backend(self, fake: FakeNvmV2) -> NvmWindowsV2Backend:
        return NvmWindowsV2Backend(
            runner=fake,
            which=lambda command: (
                ntpath.join(fake.program_root, "nvm.exe")
                if command == "nvm"
                else fake.path_node
                if command == "node"
                else None
            ),
        )

    def _desired(
        self,
        versions: tuple[str, ...],
        *,
        selected: str,
    ) -> RuntimeDesiredState:
        return RuntimeDesiredState(
            subject="node",
            backend="nvm-windows-v2",
            instances=tuple(
                nvm_windows_runtime_spec(version)
                for version in versions
            ),
            selected_key=selected,
        )

    def test_multiversion_reconcile_and_shim_metadata(self) -> None:
        fake = FakeNvmV2()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fake)
            result = reconcile_runtime(
                context,
                backend,
                self._desired(("22.20.0", "24.9.0", "26.0.0"), selected="24.9.0"),
            )
            states = read_runtime_ownerships(context, "node")
            instances = backend.discover(context)

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual({"22.20.0", "24.9.0", "26.0.0"}, set(fake.versions))
        self.assertEqual("24.9.0", fake.selected)
        self.assertEqual({"user:fixture"}, {state.scope_subject for state in states})
        managed = [item for item in instances if item.backend == "nvm-windows-v2"]
        self.assertEqual({"shim"}, {item.metadata["nvm_mode"] for item in managed})
        self.assertEqual(
            {"10.9.3", "11.6.0", "11.8.0"},
            {item.metadata["bundled_npm_version"] for item in managed},
        )

    def test_selection_uses_no_install_and_does_not_mutate_installed_set(self) -> None:
        fake = FakeNvmV2()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fake)
            reconcile_runtime(
                context,
                backend,
                self._desired(("22.20.0", "24.9.0"), selected="22.20.0"),
            )
            fake.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(("22.20.0", "24.9.0"), selected="24.9.0"),
            )

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        use_call = next(call for call in fake.calls if call[1] == "use")
        self.assertEqual(
            [
                ntpath.join(fake.program_root, "nvm.exe"),
                "use",
                "24.9.0",
                "--no-install",
            ],
            use_call,
        )
        self.assertFalse(any(call[1] == "install" for call in fake.calls))

    def test_exact_uninstall_preserves_other_versions(self) -> None:
        fake = FakeNvmV2()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fake)
            reconcile_runtime(
                context,
                backend,
                self._desired(("22.20.0", "24.9.0"), selected="24.9.0"),
            )
            fake.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(("24.9.0",), selected="24.9.0"),
            )

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual({"24.9.0"}, set(fake.versions))
        self.assertIn(
            [ntpath.join(fake.program_root, "nvm.exe"), "uninstall", "22.20.0"],
            fake.calls,
        )

    def test_unmanaged_path_node_is_visible_but_unowned(self) -> None:
        fake = FakeNvmV2()
        fake.versions["24.9.0"] = "11.6.0"
        fake.selected = "24.9.0"

        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fake)
            instances = backend.discover(context)

        unmanaged = [item for item in instances if item.backend == "node-unmanaged"]
        self.assertEqual(1, len(unmanaged))
        self.assertEqual("20.19.5", unmanaged[0].version)
        self.assertEqual(Path(r"C:\Legacy\node.exe"), unmanaged[0].executable)

    def test_manager_shim_path_is_not_reported_as_unmanaged_node(self) -> None:
        fake = FakeNvmV2()
        fake.versions["24.9.0"] = "11.6.0"
        fake.selected = "24.9.0"
        fake.path_node = ntpath.join(fake.program_root, "node.exe")

        with tempfile.TemporaryDirectory() as raw:
            instances = self._backend(fake).discover(self._context(Path(raw)))

        self.assertFalse(any(item.backend == "node-unmanaged" for item in instances))

    def test_runtime_install_does_not_request_global_module_copying(self) -> None:
        fake = FakeNvmV2()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw))
            backend = self._backend(fake)
            reconcile_runtime(
                context,
                backend,
                self._desired(("24.9.0",), selected="24.9.0"),
            )

        install_call = next(call for call in fake.calls if call[1] == "install")
        self.assertNotIn("--copy-from", install_call)
        self.assertNotIn("--from", install_call)

    def test_noncurrent_user_is_rejected_before_nvm_invocation(self) -> None:
        fake = FakeNvmV2()
        with tempfile.TemporaryDirectory() as raw:
            context = self._context(Path(raw), account="other", current=False)
            backend = self._backend(fake)
            with self.assertRaises(NvmWindowsV2Error):
                backend.discover(context)

        self.assertEqual([], fake.calls)


if __name__ == "__main__":
    unittest.main()
