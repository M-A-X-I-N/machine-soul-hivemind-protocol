from __future__ import annotations

import json
import math
import unittest

from annexation_procedures.model import OperationResult, ResultStatus
from annexation_procedures.presentation import render_human, render_json


class OperationResultTests(unittest.TestCase):
    def test_success_shape_and_exit_code(self) -> None:
        result = OperationResult.success(
            "installed",
            "Application was installed.",
            changed=True,
            data={"application": "example", "version": "1.2.3"},
        )

        self.assertEqual(ResultStatus.SUCCESS, result.status)
        self.assertTrue(result.changed)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("installed", result.code)
        self.assertEqual("example", result.data["application"])

    def test_status_exit_contract(self) -> None:
        cases = (
            (OperationResult.failure("conflict", "Destination conflicts."), 1),
            (OperationResult.unsupported("unsupported", "Platform unsupported."), 2),
            (
                OperationResult.not_implemented(
                    "not_implemented",
                    "Operation is not implemented.",
                ),
                2,
            ),
            (OperationResult.error("io_error", "Filesystem operation failed."), 3),
        )

        for result, expected in cases:
            with self.subTest(status=result.status):
                self.assertEqual(expected, result.exit_code)

    def test_non_success_may_report_partial_change(self) -> None:
        result = OperationResult.error(
            "rollback_failed",
            "Rollback was incomplete.",
            changed=True,
        )
        self.assertTrue(result.changed)
        self.assertEqual(3, result.exit_code)

    def test_code_must_be_lower_snake_case(self) -> None:
        with self.assertRaises(ValueError):
            OperationResult.success("NOT-OK", "Bad code.")

    def test_message_must_not_be_empty(self) -> None:
        with self.assertRaises(ValueError):
            OperationResult.success("ok", "   ")

    def test_data_is_read_only_and_json_compatible(self) -> None:
        source = {"count": 1}
        result = OperationResult.success("ok", "Done.", data=source)
        source["count"] = 2

        self.assertEqual(1, result.data["count"])
        with self.assertRaises(TypeError):
            result.data["count"] = 3  # type: ignore[index]

        with self.assertRaises((TypeError, ValueError)):
            OperationResult.success("bad_data", "Bad.", data={"value": object()})
        with self.assertRaises((TypeError, ValueError)):
            OperationResult.success("bad_nan", "Bad.", data={"value": math.nan})

    def test_machine_output_has_fixed_shape(self) -> None:
        result = OperationResult.failure(
            "not_applied",
            "Configuration is not applied.",
            data={"application": "example"},
        )
        payload = json.loads(render_json(result))

        self.assertEqual(
            {
                "status": "failure",
                "changed": False,
                "code": "not_applied",
                "message": "Configuration is not applied.",
                "data": {"application": "example"},
            },
            payload,
        )

    def test_human_output_is_deterministic(self) -> None:
        result = OperationResult.success("applied", "Configuration is applied.")
        self.assertEqual(
            "SUCCESS applied: Configuration is applied.",
            render_human(result),
        )


if __name__ == "__main__":
    unittest.main()
