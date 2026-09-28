from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    OperationContext,
    Platform,
    RuntimeDesiredState,
    TargetAccount,
)
from annexation_procedures.process import ProcessResult
from annexation_procedures.python_runtime import (
    PythonInstallManagerBackend,
    PythonInstallManagerError,
    python_manager_runtime_spec,
)
from annexation_procedures.runtime import read_runtime_ownerships, reconcile_runtime


def _row(manager_id: str, tag: str, version: str, *, company: str = "PythonCore"):
    return {
        "schema": 1,
        "id": manager_id,
        "tag": tag,
        "company": company,
        "sort-version": version,
        "display-name": f"{company} {version}",
        "prefix": rf"C:\Users\fixture\AppData\Local\Python\{manager_id}",
        "executable": rf"C:\Users\fixture\AppData\Local\Python\{manager_id}\python.exe",
    }


class FakePythonManager:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.catalog = {
            "pythoncore-3.13-64": _row("pythoncore-3.13-64", "3.13-64", "3.13.9"),
            "pythoncore-3.14-64": _row("pythoncore-3.14-64", "3.14-64", "3.14.7"),
        }
        self.managed: dict[str, dict[str, object]] = {}
        self.unmanaged = [
            {
                **_row("__unmanaged-Legacy-3.12", "3.12", "3.12.10", company="Legacy"),
                "unmanaged": 1,
                "prefix": r"C:\Legacy\Python312",
                "executable": r"C:\Legacy\Python312\python.exe",
            }
        ]
        self.calls: list[list[str]] = []

    def _selected(self) -> dict[str, object] | None:
        default_tag = None
        if self.config_path.is_file():
            default_tag = json.loads(
                self.config_path.read_text(encoding="utf-8")
            ).get("default_tag")
        if default_tag:
            for row in [*self.managed.values(), *self.unmanaged]:
                selection = f"{row['company']}\\{row['tag']}"
                if default_tag in {selection, row["tag"]}:
                    return row
        if self.managed:
            return sorted(
                self.managed.values(),
                key=lambda item: str(item["sort-version"]),
                reverse=True,
            )[0]
        return self.unmanaged[0] if self.unmanaged else None

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        if argv[0] != "pymanager.exe":
            return ProcessResult(99, "", "wrong executable")
        command = argv[1]
        if command == "list":
            if "--one" in argv:
                selected = self._selected()
                return ProcessResult(
                    0,
                    json.dumps({"versions": [selected] if selected else []}),
                    "",
                )
            rows = list(self.managed.values())
            if "--only-managed" not in argv:
                rows.extend(self.unmanaged)
            return ProcessResult(0, json.dumps({"versions": rows}), "")
        if command == "install":
            manager_id = argv[argv.index("--by-id") + 1]
            self.managed[manager_id] = dict(self.catalog[manager_id])
            return ProcessResult(0, "", "")
        if command == "uninstall":
            manager_id = argv[argv.index("--by-id") + 1]
            self.managed.pop(manager_id, None)
            return ProcessResult(0, "", "")
        return ProcessResult(98, "", "unexpected command")


class PythonInstallManagerBackendTests(unittest.TestCase):
    def _context(
        self,
        root: Path,
        *,
        account: str = "fixture",
        current: bool = True,
    ) -> OperationContext:
        home = root / account
        appdata = home / "AppData" / "Roaming"
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture-host",
            target_account=TargetAccount(account, home, current),
            environment={"APPDATA": str(appdata)},
        )

    def _backend(self, fake: FakePythonManager) -> PythonInstallManagerBackend:
        return PythonInstallManagerBackend(
            runner=fake,
            which=lambda command: (
                "pymanager.exe"
                if command == "pymanager"
                else r"C:\Legacy\py.exe"
                if command == "py"
                else None
            ),
        )

    def _desired(
        self,
        *,
        selected: str,
        ids: tuple[str, ...] = (
            "pythoncore-3.13-64",
            "pythoncore-3.14-64",
        ),
    ) -> RuntimeDesiredState:
        versions = {
            "pythoncore-3.13-64": "3.13",
            "pythoncore-3.14-64": "3.14",
        }
        return RuntimeDesiredState(
            subject="python",
            backend="python-install-manager",
            instances=tuple(
                python_manager_runtime_spec(
                    manager_id,
                    version=versions[manager_id],
                    architecture="x64",
                    distribution="PythonCore",
                )
                for manager_id in ids
            ),
            selected_key=selected,
        )

    def test_multiversion_reconcile_uses_exact_manager_ids_and_user_scope(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            config = Path(context.environment["APPDATA"]) / "Python" / "pymanager.json"
            fake = FakePythonManager(config)
            backend = self._backend(fake)

            result = reconcile_runtime(
                context,
                backend,
                self._desired(selected="pythoncore-3.14-64"),
            )
            states = read_runtime_ownerships(context, "python")
            self.assertTrue(config.is_file(), result.to_dict())
            default_tag = json.loads(config.read_text(encoding="utf-8"))["default_tag"]

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertEqual(
            {"pythoncore-3.13-64", "pythoncore-3.14-64"},
            set(fake.managed),
        )
        self.assertEqual({"user:fixture"}, {state.scope_subject for state in states})
        self.assertEqual("PythonCore\\3.14-64", default_tag)
        install_calls = [call for call in fake.calls if call[1] == "install"]
        self.assertEqual(2, len(install_calls))
        self.assertTrue(all("--by-id" in call for call in install_calls))

    def test_default_only_change_does_not_reinstall(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            config = Path(context.environment["APPDATA"]) / "Python" / "pymanager.json"
            fake = FakePythonManager(config)
            backend = self._backend(fake)
            reconcile_runtime(
                context,
                backend,
                self._desired(selected="pythoncore-3.13-64"),
            )
            fake.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(selected="pythoncore-3.14-64"),
            )
            self.assertTrue(config.is_file(), result.to_dict())
            default_tag = json.loads(config.read_text(encoding="utf-8"))["default_tag"]

        self.assertEqual("runtime_reconciled", result.code, result.to_dict())
        self.assertFalse(
            any(call[1] in {"install", "uninstall"} for call in fake.calls)
        )
        self.assertEqual("PythonCore\\3.14-64", default_tag)

    def test_exact_uninstall_uses_by_id_and_preserves_other_version(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            config = Path(context.environment["APPDATA"]) / "Python" / "pymanager.json"
            fake = FakePythonManager(config)
            backend = self._backend(fake)
            reconcile_runtime(
                context,
                backend,
                self._desired(selected="pythoncore-3.14-64"),
            )
            fake.calls.clear()

            result = reconcile_runtime(
                context,
                backend,
                self._desired(
                    selected="pythoncore-3.14-64",
                    ids=("pythoncore-3.14-64",),
                ),
            )

        self.assertEqual("runtime_reconciled", result.code)
        self.assertEqual({"pythoncore-3.14-64"}, set(fake.managed))
        uninstall = next(call for call in fake.calls if call[1] == "uninstall")
        self.assertEqual(
            "pythoncore-3.13-64",
            uninstall[uninstall.index("--by-id") + 1],
        )

    def test_unmanaged_legacy_runtime_is_visible_but_never_owned(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            config = Path(context.environment["APPDATA"]) / "Python" / "pymanager.json"
            fake = FakePythonManager(config)
            backend = self._backend(fake)

            instances = backend.discover(context)
            reconcile_runtime(
                context,
                backend,
                RuntimeDesiredState(
                    subject="python",
                    backend="python-install-manager",
                    instances=(
                        python_manager_runtime_spec(
                            "pythoncore-3.14-64",
                            version="3.14",
                            architecture="x64",
                        ),
                    ),
                    selected_key="pythoncore-3.14-64",
                ),
            )
            states = read_runtime_ownerships(context, "python")

        legacy = next(item for item in instances if item.backend == "python-unmanaged")
        self.assertEqual("__unmanaged-Legacy-3.12", legacy.backend_key)
        self.assertNotIn(
            "__unmanaged-Legacy-3.12",
            {state.backend_key for state in states},
        )

    def test_legacy_py_collision_is_ignored_in_favor_of_pymanager(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            config = Path(context.environment["APPDATA"]) / "Python" / "pymanager.json"
            fake = FakePythonManager(config)
            backend = self._backend(fake)

            backend.discover(context)

        self.assertTrue(fake.calls)
        self.assertTrue(all(call[0] == "pymanager.exe" for call in fake.calls))

    def test_noncurrent_user_is_rejected_before_manager_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, account="other", current=False)
            config = (
                root
                / "other"
                / "AppData"
                / "Roaming"
                / "Python"
                / "pymanager.json"
            )
            fake = FakePythonManager(config)
            backend = self._backend(fake)

            with self.assertRaises(PythonInstallManagerError):
                backend.discover(context)

        self.assertEqual([], fake.calls)


if __name__ == "__main__":
    unittest.main()
