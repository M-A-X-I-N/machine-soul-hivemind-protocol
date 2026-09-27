"""Native primitive process boundary."""

from .protocol import (
    PROTOCOL_VERSION,
    PrimitiveProcessError,
    PrimitiveProtocolError,
    build_primitive_envelope,
    normalize_primitive_process,
    parse_primitive_response,
)

__all__ = [
    "PROTOCOL_VERSION",
    "PrimitiveProcessError",
    "PrimitiveProtocolError",
    "build_primitive_envelope",
    "normalize_primitive_process",
    "parse_primitive_response",
]
