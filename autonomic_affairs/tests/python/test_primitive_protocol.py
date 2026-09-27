from __future__ import annotations

import json
import unittest

from accumulated_instruments.machine_soul.model import OperationResult, ResultStatus
from accumulated_instruments.machine_soul.primitives import (
    PROTOCOL_VERSION,
    PrimitiveProcessError,
    PrimitiveProtocolError,
    build_primitive_envelope,
    normalize_primitive_process,
    parse_primitive_response,
)


class PrimitiveProtocolTests(unittest.TestCase):
    def _json(self, primitive: str, result: OperationResult) -> str:
        return json.dumps(build_primitive_envelope(primitive, result))

    def test_valid_response_normalizes_to_operation_result(self) -> None:
        source = OperationResult.success(
            "symlink_created",
            "Symbolic link was created.",
            changed=True,
            data={"destination": "example"},
        )

        parsed = parse_primitive_response(
            self._json("create_symlink", source),
            expected_primitive="create_symlink",
        )

        self.assertEqual(ResultStatus.SUCCESS, parsed.status)
        self.assertEqual("symlink_created", parsed.code)
        self.assertTrue(parsed.changed)

    def test_semantic_failure_is_valid_process_success(self) -> None:
        source = OperationResult.error(
            "permission_denied",
            "Native action was denied.",
            changed=False,
        )
        result = normalize_primitive_process(
            returncode=0,
            stdout=self._json("create_symlink", source),
            stderr="diagnostic text is not protocol",
            expected_primitive="create_symlink",
        )

        self.assertEqual(ResultStatus.ERROR, result.status)
        self.assertEqual(3, result.exit_code)

    def test_partial_change_semantic_error_is_preserved(self) -> None:
        source = OperationResult.error(
            "partial_change",
            "Mutation partially completed.",
            changed=True,
        )
        parsed = parse_primitive_response(
            self._json("native_action", source),
            expected_primitive="native_action",
        )
        self.assertTrue(parsed.changed)

    def test_nonzero_process_exit_is_not_a_semantic_result(self) -> None:
        valid_stdout = self._json(
            "create_symlink",
            OperationResult.success("ok", "Done."),
        )
        with self.assertRaises(PrimitiveProcessError) as ctx:
            normalize_primitive_process(
                returncode=7,
                stdout=valid_stdout,
                stderr="boom",
                expected_primitive="create_symlink",
            )

        self.assertEqual(7, ctx.exception.returncode)
        self.assertEqual("boom", ctx.exception.stderr)

    def test_empty_or_malformed_stdout_is_protocol_failure(self) -> None:
        for payload in ("", "not json", "{} trailing"):
            with self.subTest(payload=payload):
                with self.assertRaises(PrimitiveProtocolError):
                    parse_primitive_response(
                        payload,
                        expected_primitive="create_symlink",
                    )

    def test_protocol_version_is_strict(self) -> None:
        payload = build_primitive_envelope(
            "create_symlink",
            OperationResult.success("ok", "Done."),
        )
        payload["protocol_version"] = PROTOCOL_VERSION + 1

        with self.assertRaises(PrimitiveProtocolError):
            parse_primitive_response(
                json.dumps(payload),
                expected_primitive="create_symlink",
            )

    def test_primitive_name_must_match_invocation(self) -> None:
        stdout = self._json(
            "remove_symlink",
            OperationResult.success("ok", "Done."),
        )
        with self.assertRaises(PrimitiveProtocolError):
            parse_primitive_response(
                stdout,
                expected_primitive="create_symlink",
            )

    def test_envelope_and_result_fields_are_strict(self) -> None:
        envelope = build_primitive_envelope(
            "create_symlink",
            OperationResult.success("ok", "Done."),
        )
        envelope["surprise"] = True

        with self.assertRaises(PrimitiveProtocolError):
            parse_primitive_response(
                json.dumps(envelope),
                expected_primitive="create_symlink",
            )

        bad_result = build_primitive_envelope(
            "create_symlink",
            OperationResult.success("ok", "Done."),
        )
        assert isinstance(bad_result["result"], dict)
        bad_result["result"]["surprise"] = True

        with self.assertRaises(PrimitiveProtocolError):
            parse_primitive_response(
                json.dumps(bad_result),
                expected_primitive="create_symlink",
            )


if __name__ == "__main__":
    unittest.main()
