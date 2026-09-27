"""Deterministic presentation of common operation results."""

from __future__ import annotations

import json

from .model import OperationResult


def render_human(result: OperationResult) -> str:
    """Render the canonical concise human-facing one-line result."""
    return f"{result.status.value.upper()} {result.code}: {result.message}"


def render_json(result: OperationResult) -> str:
    """Render deterministic compact JSON for automation/process consumers."""
    return json.dumps(
        result.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
