from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from accumulated_instruments.machine_soul.model import (
    ConflictPolicy,
    Operation,
    OperationContext,
    OperationResult,
    Platform,
    TargetAccount,
)
from accumulated_instruments.machine_soul.presentation import wrapper_main


EXPECTED_OPERATIONS = {
    "apply_config.py": Operation.APPLY_CONFIG,
    "unapply_config.py": Operation.UNAPPLY_CONFIG,
    "check_config.py": Operation.CHECK_CONFIG,
    "install.py": Operation.INSTALL,
    "uninstall.py": Operation.UNINSTALL,
    "check_installed.py": Operation.CHECK_INSTALLED,
}

EXPECTED_APPLICATIONS = {
    "bash",
    "cmd",
    "contour",
    "fish",
    "oh_my_posh",
    "powershell",
    "windows_terminal",
    "zsh",
}


def _load_wrapper(path: Path):
    name = "_machine_soul_wrapper_" + "_".join(path.parts[-3:]).replace(".", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AtomicWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[3]
        cls.annexation = cls.root / "annexation_procedures"

    def test_every_current_application_exposes_uniform_atomic_wrappers(self) -> None:
        applications = {
            path.name
            for path in self.annexation.iterdir()
            if path.is_dir() and (path / "_application.py").is_file()
        }
        self.assertEqual(EXPECTED_APPLICATIONS, applications)

        for application in sorted(applications):
            directory = self.annexation / application
            for filename in EXPECTED_OPERATIONS:
                with self.subTest(application=application, wrapper=filename):
                    self.assertTrue((directory / filename).is_file())

    def test_imported_run_is_only_application_operation_binding(self) -> None:
        for application in sorted(EXPECTED_APPLICATIONS):
            directory = self.annexation / application
            for filename, expected_operation in EXPECTED_OPERATIONS.items():
                with self.subTest(application=application, wrapper=filename):
                    module = _load_wrapper(directory / filename)
                    sentinel_context = object()
                    sentinel_result = OperationResult.success("sentinel", "sentinel")
                    calls = []

                    def fake_perform(declaration, operation, context):
                        calls.append((declaration, operation, context))
                        return sentinel_result

                    module.perform_operation = fake_perform
                    self.assertIs(sentinel_result, module.run(sentinel_context))
                    self.assertEqual(
                        [(module.APPLICATION, expected_operation, sentinel_context)],
                        calls,
                    )
                    self.assertEqual(expected_operation, module.OPERATION)

    def test_every_wrapper_is_directly_runnable_from_an_unrelated_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            for application in sorted(EXPECTED_APPLICATIONS):
                directory = self.annexation / application
                for filename in EXPECTED_OPERATIONS:
                    wrapper = directory / filename
                    with self.subTest(application=application, wrapper=filename):
                        result = subprocess.run(
                            [sys.executable, str(wrapper), "--help"],
                            cwd=temp,
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=False,
                        )
                        self.assertEqual(0, result.returncode, result.stderr)
                        self.assertIn("--account", result.stdout)
                        self.assertIn("--dry-run", result.stdout)
                        self.assertIn("--json", result.stdout)


class WrapperMainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = OperationContext(
            repository_root=Path.cwd(),
            platform=Platform.LINUX,
            host="test-host",
            target_account=TargetAccount("maintainer", Path.cwd(), True),
            conflict_policy=ConflictPolicy.ABORT,
        )

    def test_common_options_build_context_and_render_json(self) -> None:
        seen = []

        def run(context):
            seen.append(context)
            return OperationResult.success("ok", "worked")

        output = StringIO()
        with patch(
            "accumulated_instruments.machine_soul.presentation.build_operation_context",
            return_value=self.context,
        ) as build, redirect_stdout(output):
            code = wrapper_main(
                run,
                [
                    "--account",
                    "maintainer",
                    "--dry-run",
                    "--conflict-policy",
                    "abort",
                    "--json",
                ],
            )

        self.assertEqual(0, code)
        self.assertEqual([self.context], seen)
        build.assert_called_once_with(
            target_account="maintainer",
            dry_run=True,
            conflict_policy=ConflictPolicy.ABORT,
        )
        self.assertIn('"code":"ok"', output.getvalue())

    def test_prompt_confirmation_retries_with_replace_policy(self) -> None:
        prompt_context = OperationContext(
            repository_root=Path.cwd(),
            platform=Platform.LINUX,
            host="test-host",
            target_account=TargetAccount("maintainer", Path.cwd(), True),
            conflict_policy=ConflictPolicy.PROMPT,
        )
        seen = []

        def run(context):
            seen.append(context)
            if len(seen) == 1:
                return OperationResult.failure(
                    "confirmation_required",
                    "confirmation required",
                )
            return OperationResult.success("applied", "applied", changed=True)

        with patch(
            "accumulated_instruments.machine_soul.presentation.build_operation_context",
            return_value=prompt_context,
        ), patch("builtins.input", return_value="yes"), redirect_stdout(StringIO()):
            code = wrapper_main(run, [])

        self.assertEqual(0, code)
        self.assertEqual(2, len(seen))
        self.assertEqual(ConflictPolicy.PROMPT, seen[0].conflict_policy)
        self.assertEqual(
            ConflictPolicy.BACKUP_AND_REPLACE,
            seen[1].conflict_policy,
        )

    def test_prompt_decline_does_not_retry(self) -> None:
        prompt_context = OperationContext(
            repository_root=Path.cwd(),
            platform=Platform.LINUX,
            host="test-host",
            target_account=TargetAccount("maintainer", Path.cwd(), True),
            conflict_policy=ConflictPolicy.PROMPT,
        )
        calls = 0

        def run(context):
            nonlocal calls
            calls += 1
            return OperationResult.failure(
                "confirmation_required",
                "confirmation required",
            )

        output = StringIO()
        with patch(
            "accumulated_instruments.machine_soul.presentation.build_operation_context",
            return_value=prompt_context,
        ), patch("builtins.input", return_value="no"), redirect_stdout(output):
            code = wrapper_main(run, [])

        self.assertEqual(1, code)
        self.assertEqual(1, calls)
        self.assertIn("declined", output.getvalue())


if __name__ == "__main__":
    unittest.main()
