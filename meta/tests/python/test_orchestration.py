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

from annexation_procedures.model import (
    ConflictPolicy,
    Operation,
    OperationContext,
    OperationResult,
    Platform,
    ResultStatus,
    TargetAccount,
)
from annexation_procedures.orchestration import (
    WrapperBinding,
    apply_installed_configurations,
    apply_selected_configurations,
    check_all_configurations,
    discover_wrappers,
    execute_bindings,
)


def _binding(app: str, operation: Operation, run) -> WrapperBinding:
    return WrapperBinding(
        application_id=app,
        display_name=app.title(),
        operation=operation,
        path=Path(f"/{app}/{operation.value}.py"),
        run=run,
    )


class OrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = OperationContext(
            repository_root=Path.cwd(),
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", Path.cwd(), True),
            conflict_policy=ConflictPolicy.ABORT,
        )

    def test_check_all_invokes_only_check_wrappers_and_preserves_order(self) -> None:
        calls = []

        def run_a(context):
            calls.append(("a", context))
            return OperationResult.success("applied", "a")

        def run_b(context):
            calls.append(("b", context))
            return OperationResult.failure("not_applied", "b")

        unrelated_calls = []

        bindings = (
            _binding("a", Operation.CHECK_CONFIG, run_a),
            _binding("a", Operation.APPLY_CONFIG, lambda context: unrelated_calls.append(context)),
            _binding("b", Operation.CHECK_CONFIG, run_b),
        )
        report = check_all_configurations(bindings, self.context)

        self.assertEqual([("a", self.context), ("b", self.context)], calls)
        self.assertEqual([], unrelated_calls)
        self.assertEqual(["a", "b"], [attempt.application_id for attempt in report.attempts])
        self.assertEqual(["applied", "not_applied"], [attempt.result.code for attempt in report.attempts])
        self.assertEqual(1, report.exit_code)

    def test_selected_apply_calls_only_selected_application(self) -> None:
        calls = []
        bindings = (
            _binding("a", Operation.APPLY_CONFIG, lambda context: calls.append("a") or OperationResult.success("applied", "a")),
            _binding("b", Operation.APPLY_CONFIG, lambda context: calls.append("b") or OperationResult.success("applied", "b")),
        )

        report = apply_selected_configurations(bindings, self.context, ["b"])

        self.assertEqual(["b"], calls)
        self.assertEqual(["b"], [attempt.application_id for attempt in report.attempts])

    def test_installed_only_workflow_uses_check_wrapper_before_apply(self) -> None:
        calls = []

        def result(app, operation, code, status=ResultStatus.SUCCESS):
            calls.append((app, operation))
            if status is ResultStatus.SUCCESS:
                return OperationResult.success(code, code)
            return OperationResult.failure(code, code)

        bindings = (
            _binding("a", Operation.CHECK_INSTALLED, lambda context: result("a", "check", "installed_unmanaged", ResultStatus.FAILURE)),
            _binding("a", Operation.APPLY_CONFIG, lambda context: result("a", "apply", "applied")),
            _binding("b", Operation.CHECK_INSTALLED, lambda context: result("b", "check", "not_installed")),
            _binding("b", Operation.APPLY_CONFIG, lambda context: result("b", "apply", "applied")),
        )

        report = apply_installed_configurations(bindings, self.context)

        self.assertEqual(
            [("a", "check"), ("a", "apply"), ("b", "check")],
            calls,
        )
        self.assertEqual(
            [
                ("a", Operation.CHECK_INSTALLED),
                ("a", Operation.APPLY_CONFIG),
                ("b", Operation.CHECK_INSTALLED),
            ],
            [(attempt.application_id, attempt.operation) for attempt in report.attempts],
        )

    def test_partial_change_non_success_stops_later_mutation(self) -> None:
        calls = []

        def first(context):
            calls.append("first")
            return OperationResult.error("partial_change", "danger", changed=True)

        def second(context):
            calls.append("second")
            return OperationResult.success("applied", "second", changed=True)

        report = execute_bindings(
            (
                _binding("a", Operation.APPLY_CONFIG, first),
                _binding("b", Operation.APPLY_CONFIG, second),
            ),
            self.context,
        )

        self.assertEqual(["first"], calls)
        self.assertEqual(1, len(report.attempts))
        self.assertTrue(report.changed)
        self.assertEqual(3, report.exit_code)

    def test_confirmation_is_resolved_by_orchestration_not_engine(self) -> None:
        seen = []

        def run(context):
            seen.append(context.conflict_policy)
            if context.conflict_policy is ConflictPolicy.PROMPT:
                return OperationResult.failure("confirmation_required", "confirm")
            return OperationResult.success("applied", "applied", changed=True)

        prompt_context = OperationContext(
            repository_root=self.context.repository_root,
            platform=self.context.platform,
            host=self.context.host,
            target_account=self.context.target_account,
            conflict_policy=ConflictPolicy.PROMPT,
        )
        report = execute_bindings(
            (_binding("a", Operation.APPLY_CONFIG, run),),
            prompt_context,
            confirm_replacement=lambda binding, result: True,
        )

        self.assertEqual(
            [ConflictPolicy.PROMPT, ConflictPolicy.BACKUP_AND_REPLACE],
            seen,
        )
        self.assertEqual("applied", report.attempts[0].result.code)


class RealOrchestratorSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[3]
        cls.manager = cls.root / "annexation_procedures/manage_machine_soul.py"

    def test_discovery_finds_every_current_atomic_wrapper(self) -> None:
        bindings = discover_wrappers(self.root)
        self.assertEqual(84, len(bindings))
        self.assertEqual(12, len({binding.application_id for binding in bindings}))
        for application_id in {binding.application_id for binding in bindings}:
            self.assertEqual(
                set(Operation),
                {binding.operation for binding in bindings if binding.application_id == application_id},
            )

    def test_manager_list_runs_from_unrelated_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(self.manager), "--workflow", "list"],
                cwd=temp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("fish (Fish)", result.stdout)
        self.assertIn("windows_terminal (Windows Terminal)", result.stdout)
        self.assertIn("verify_config", result.stdout)

    def test_interactive_exit_performs_no_operation(self) -> None:
        spec = importlib.util.spec_from_file_location("_machine_soul_manager_test", self.manager)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        output = StringIO()
        with patch("builtins.input", return_value="5"), redirect_stdout(output):
            code = module.main([])

        self.assertEqual(0, code)
        self.assertIn("No operations were performed.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
