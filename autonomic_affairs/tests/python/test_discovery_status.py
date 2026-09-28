from __future__ import annotations

import json
from pathlib import Path
import unittest

from annexation_procedures.model import (
    Operation,
    OperationContext,
    OperationResult,
    Platform,
    ResultStatus,
    TargetAccount,
)
from annexation_procedures.orchestration import (
    WrapperBinding,
    discovery_status,
)
from annexation_procedures.status_presentation import (
    render_discovery_status_human,
    render_discovery_status_json,
)


def _binding(app: str, operation: Operation, result: OperationResult, calls: list):
    def run(context):
        calls.append((app, operation, context))
        return result

    return WrapperBinding(
        application_id=app,
        display_name=app.replace("_", " ").title(),
        operation=operation,
        path=Path(f"/{app}/{operation.value}.py"),
        run=run,
    )


def _installation(
    *,
    presence: str,
    code: str,
    candidates: list[dict[str, object]] | None = None,
    ownership: str = "unknown",
) -> OperationResult:
    data = {
        "assessment": {
            "presence": presence,
            "candidates": candidates or [],
            "preferred_candidate_index": None,
            "machine_soul_state": ownership,
            "observations": [],
            "errors": [],
        }
    }
    if presence == "present":
        return OperationResult.failure(code, "installation state", data=data)
    if presence == "ambiguous":
        return OperationResult.failure(code, "ambiguous installation", data=data)
    return OperationResult.failure(code, "installation state", data=data)


def _configuration(code: str, *, ownership: str | None = None) -> OperationResult:
    data = {"structural_state": code}
    if ownership is not None:
        data["ownership_state"] = ownership
    if code == "applied":
        return OperationResult.success(code, "structural state", data=data)
    return OperationResult.failure(code, "structural state", data=data)


def _effective(conclusion: str, evidence: str) -> OperationResult:
    data = {
        "assessment": {
            "conclusion": conclusion,
            "strongest_evidence": evidence,
            "observations": [],
            "errors": [],
        }
    }
    if conclusion == "effective":
        return OperationResult.success("config_effective", "effective", data=data)
    if conclusion == "not_effective":
        return OperationResult.failure("config_not_effective", "not effective", data=data)
    return OperationResult.failure("verification_indeterminate", "indeterminate", data=data)


class DiscoveryStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = OperationContext(
            repository_root=Path.cwd(),
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", Path.cwd(), True),
        )

    def test_representative_three_dimension_scenarios_remain_independent(self) -> None:
        calls: list = []
        scenarios = {
            "foreign_effective": (
                _installation(
                    presence="present",
                    code="installed_unmanaged",
                    candidates=[
                        {
                            "native_identity": "foreign",
                            "preferred_match": "no",
                            "ownership": "unmanaged",
                        }
                    ],
                    ownership="unmanaged",
                ),
                _configuration("applied", ownership="managed"),
                _effective("effective", "runtime"),
            ),
            "applied_ineffective": (
                _installation(
                    presence="present",
                    code="installed_unmanaged",
                    candidates=[
                        {
                            "native_identity": "preferred",
                            "preferred_match": "yes",
                            "ownership": "unmanaged",
                        }
                    ],
                    ownership="unmanaged",
                ),
                _configuration("applied", ownership="managed"),
                _effective("not_effective", "runtime"),
            ),
            "staged_absent": (
                _installation(presence="absent", code="not_installed"),
                _configuration("applied", ownership="managed"),
                _effective("indeterminate", "none"),
            ),
            "ambiguous_install": (
                _installation(
                    presence="ambiguous",
                    code="installed_ambiguous",
                    candidates=[
                        {"native_identity": "one", "preferred_match": "yes"},
                        {"native_identity": "two", "preferred_match": "unknown"},
                    ],
                    ownership="unmanaged",
                ),
                _configuration("not_applied"),
                _effective("indeterminate", "resolution"),
            ),
            "unverifiable_runtime": (
                _installation(
                    presence="present",
                    code="installed_unmanaged",
                    candidates=[
                        {"native_identity": "example", "preferred_match": "unknown"}
                    ],
                    ownership="unmanaged",
                ),
                _configuration("applied", ownership="unrecorded"),
                _effective("indeterminate", "application"),
            ),
        }

        bindings = []
        direct: dict[tuple[str, Operation], dict[str, object]] = {}
        for app, results in scenarios.items():
            for operation, result in zip(
                (
                    Operation.CHECK_INSTALLED,
                    Operation.CHECK_CONFIG,
                    Operation.VERIFY_CONFIG,
                ),
                results,
            ):
                bindings.append(_binding(app, operation, result, calls))
                direct[(app, operation)] = result.to_dict()

        report = discovery_status(bindings, self.context)

        self.assertEqual(5, len(report.applications))
        self.assertEqual(15, len(calls))
        self.assertEqual(0, report.exit_code)

        for entry in report.applications:
            self.assertEqual(
                direct[(entry.application_id, Operation.CHECK_INSTALLED)],
                entry.installation.result.to_dict(),
            )
            self.assertEqual(
                direct[(entry.application_id, Operation.CHECK_CONFIG)],
                entry.configuration.result.to_dict(),
            )
            self.assertEqual(
                direct[(entry.application_id, Operation.VERIFY_CONFIG)],
                entry.effective.result.to_dict(),
            )

        payload = json.loads(render_discovery_status_json(report))
        self.assertEqual(5, len(payload["applications"]))
        indexed = {item["application"]: item for item in payload["applications"]}
        self.assertEqual(
            "installed_unmanaged",
            indexed["foreign_effective"]["installation"]["code"],
        )
        self.assertEqual(
            "config_not_effective",
            indexed["applied_ineffective"]["effective"]["code"],
        )
        self.assertEqual(
            "applied",
            indexed["staged_absent"]["configuration"]["code"],
        )
        self.assertEqual(
            2,
            len(indexed["ambiguous_install"]["installation"]["data"]["assessment"]["candidates"]),
        )
        self.assertEqual(
            "indeterminate",
            indexed["unverifiable_runtime"]["effective"]["data"]["assessment"]["conclusion"],
        )

    def test_human_status_names_each_dimension_without_verdict(self) -> None:
        calls: list = []
        bindings = (
            _binding(
                "example",
                Operation.CHECK_INSTALLED,
                _installation(
                    presence="present",
                    code="installed_unmanaged",
                    candidates=[
                        {
                            "native_identity": "example",
                            "preferred_match": "yes",
                            "ownership": "unmanaged",
                        }
                    ],
                    ownership="unmanaged",
                ),
                calls,
            ),
            _binding(
                "example",
                Operation.CHECK_CONFIG,
                _configuration("applied", ownership="managed"),
                calls,
            ),
            _binding(
                "example",
                Operation.VERIFY_CONFIG,
                _effective("effective", "runtime"),
                calls,
            ),
        )

        output = render_discovery_status_human(
            discovery_status(bindings, self.context)
        )

        self.assertIn("installation: present", output)
        self.assertIn("preferred_match[yes=1,no=0,unknown=0]", output)
        self.assertIn("ownership=unmanaged", output)
        self.assertIn("configuration: applied; ownership=managed", output)
        self.assertIn("effective: effective; evidence=runtime", output)
        self.assertNotIn("healthy", output.casefold())
        self.assertNotIn("score", output.casefold())

    def test_not_implemented_dimension_is_explicit_but_not_workflow_failure(self) -> None:
        calls: list = []
        bindings = (
            _binding(
                "example",
                Operation.CHECK_INSTALLED,
                OperationResult.not_implemented(
                    "operation_not_implemented",
                    "not ready",
                ),
                calls,
            ),
            _binding(
                "example",
                Operation.CHECK_CONFIG,
                _configuration("not_applied"),
                calls,
            ),
            _binding(
                "example",
                Operation.VERIFY_CONFIG,
                OperationResult.unsupported(
                    "operation_unsupported",
                    "not applicable",
                ),
                calls,
            ),
        )

        report = discovery_status(bindings, self.context)
        output = render_discovery_status_human(report)

        self.assertEqual(0, report.exit_code)
        self.assertIn("not_implemented (operation_not_implemented)", output)
        self.assertIn("unsupported (operation_unsupported)", output)

    def test_actual_operation_error_makes_status_workflow_fail(self) -> None:
        calls: list = []
        bindings = (
            _binding(
                "example",
                Operation.CHECK_INSTALLED,
                OperationResult.error("probe_failed", "boom"),
                calls,
            ),
            _binding("example", Operation.CHECK_CONFIG, _configuration("not_applied"), calls),
            _binding("example", Operation.VERIFY_CONFIG, _effective("indeterminate", "none"), calls),
        )

        report = discovery_status(bindings, self.context)

        self.assertEqual(3, report.exit_code)

    def test_missing_status_wrapper_is_visible(self) -> None:
        calls: list = []
        bindings = (
            _binding("example", Operation.CHECK_CONFIG, _configuration("applied"), calls),
            _binding("example", Operation.VERIFY_CONFIG, _effective("effective", "resolution"), calls),
        )

        report = discovery_status(bindings, self.context)
        entry = report.applications[0]

        self.assertEqual("operation_wrapper_missing", entry.installation.result.code)
        self.assertEqual(ResultStatus.NOT_IMPLEMENTED, entry.installation.result.status)


if __name__ == "__main__":
    unittest.main()
