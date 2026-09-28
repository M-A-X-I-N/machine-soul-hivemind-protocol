"""Native primitive process boundary."""

from .invoke import invoke_primitive
from .protocol import (
    PROTOCOL_VERSION,
    PrimitiveProcessError,
    PrimitiveProtocolError,
    build_primitive_envelope,
    normalize_primitive_process,
    parse_primitive_response,
)

__all__ = [
    "invoke_primitive",
    "PROTOCOL_VERSION",
    "PrimitiveProcessError",
    "PrimitiveProtocolError",
    "build_primitive_envelope",
    "normalize_primitive_process",
    "parse_primitive_response",
]
