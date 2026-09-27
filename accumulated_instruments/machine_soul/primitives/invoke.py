"""Subprocess invocation for versioned native primitives."""

from __future__ import annotations

import subprocess
from typing import Sequence

from .protocol import PrimitiveProcessError, normalize_primitive_process
from ..model import OperationResult


def invoke_primitive(
    primitive: str,
    argv: Sequence[str],
    *,
    timeout: float | None = None,
) -> OperationResult:
    """Run one native primitive without a shell and normalize its v1 response."""
    if not argv:
        raise ValueError("argv cannot be empty.")

    try:
        completed = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise PrimitiveProcessError(-1, f"Primitive timed out: {exc}") from exc
    except OSError as exc:
        raise PrimitiveProcessError(-1, f"Primitive could not be started: {exc}") from exc

    return normalize_primitive_process(
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        expected_primitive=primitive,
    )
