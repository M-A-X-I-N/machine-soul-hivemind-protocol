from __future__ import annotations

import json
import sys
import unittest

from accumulated_instruments.machine_soul.model import OperationResult
from accumulated_instruments.machine_soul.primitives import (
    PrimitiveProcessError,
    PrimitiveProtocolError,
    build_primitive_envelope,
    invoke_primitive,
)


class PrimitiveInvocationTests(unittest.TestCase):
    def test_invokes_process_without_shell_and_normalizes_result(self) -> None:
        expected = OperationResult.success("done", "Primitive completed.", changed=True)
        payload = json.dumps(build_primitive_envelope("fixture_primitive", expected))
        script = f"print({payload!r})"
        actual = invoke_primitive(
            "fixture_primitive",
            [sys.executable, "-c", script],
        )
        self.assertEqual(expected, actual)

    def test_nonzero_process_exit_is_not_trusted(self) -> None:
        with self.assertRaises(PrimitiveProcessError) as caught:
            invoke_primitive(
                "fixture_primitive",
                [sys.executable, "-c", "import sys; sys.exit(7)"],
            )
        self.assertEqual(7, caught.exception.returncode)

    def test_malformed_stdout_is_protocol_failure(self) -> None:
        with self.assertRaises(PrimitiveProtocolError):
            invoke_primitive(
                "fixture_primitive",
                [sys.executable, "-c", "print('hello human')"],
            )


if __name__ == "__main__":
    unittest.main()
