"""Versioned native-primitive response protocol."""

from __future__ import annotations

import json
import re
from typing import Mapping

from ..model import OperationResult


PROTOCOL_VERSION = 1
_PRIMITIVE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_ENVELOPE_FIELDS = {"protocol_version", "primitive", "result"}


class PrimitiveProtocolError(RuntimeError):
    """The primitive process exited normally but did not speak the protocol."""


class PrimitiveProcessError(RuntimeError):
    """The primitive process itself failed, so semantic stdout is untrusted."""

    def __init__(self, returncode: int, stderr: str = "") -> None:
        super().__init__(f"Native primitive process exited with code {returncode}.")
        self.returncode = returncode
        self.stderr = stderr


def _validate_primitive_name(name: str) -> None:
    if not _PRIMITIVE_NAME.fullmatch(name):
        raise PrimitiveProtocolError("Primitive name must be lower_snake_case.")


def build_primitive_envelope(
    primitive: str,
    result: OperationResult,
) -> dict[str, object]:
    """Build the exact protocol-v1 response envelope."""
    _validate_primitive_name(primitive)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "primitive": primitive,
        "result": result.to_dict(),
    }


def parse_primitive_response(
    stdout: str,
    *,
    expected_primitive: str,
) -> OperationResult:
    """Parse and validate one protocol-v1 JSON response from stdout."""
    _validate_primitive_name(expected_primitive)

    if not stdout.strip():
        raise PrimitiveProtocolError("Primitive produced no protocol output.")

    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise PrimitiveProtocolError("Primitive stdout is not one valid JSON value.") from exc

    if not isinstance(payload, dict):
        raise PrimitiveProtocolError("Primitive response must be a JSON object.")

    if set(payload) != _ENVELOPE_FIELDS:
        missing = _ENVELOPE_FIELDS - set(payload)
        extra = set(payload) - _ENVELOPE_FIELDS
        raise PrimitiveProtocolError(
            f"Primitive envelope fields mismatch; missing={sorted(missing)}, extra={sorted(extra)}."
        )

    version = payload["protocol_version"]
    if type(version) is not int or version != PROTOCOL_VERSION:
        raise PrimitiveProtocolError(
            f"Unsupported primitive protocol version: {version!r}."
        )

    primitive = payload["primitive"]
    if not isinstance(primitive, str):
        raise PrimitiveProtocolError("Primitive envelope name must be a string.")
    _validate_primitive_name(primitive)
    if primitive != expected_primitive:
        raise PrimitiveProtocolError(
            f"Primitive response name {primitive!r} does not match expected {expected_primitive!r}."
        )

    result_payload = payload["result"]
    if not isinstance(result_payload, Mapping):
        raise PrimitiveProtocolError("Primitive result must be a JSON object.")

    try:
        return OperationResult.from_dict(result_payload)
    except (TypeError, ValueError) as exc:
        raise PrimitiveProtocolError("Primitive result does not match OperationResult.") from exc


def normalize_primitive_process(
    *,
    returncode: int,
    stdout: str,
    stderr: str,
    expected_primitive: str,
) -> OperationResult:
    """Normalize a completed primitive process into the semantic result model."""
    if returncode != 0:
        raise PrimitiveProcessError(returncode, stderr)

    return parse_primitive_response(stdout, expected_primitive=expected_primitive)
