"""Shared Machine-Soul Python runtime.

The package is intentionally side-effect free on import. Executable wrappers
and orchestrators call into library modules; application and platform policy
does not belong in this module.
"""

from __future__ import annotations

import sys

MINIMUM_PYTHON = (3, 10)


def require_supported_python() -> None:
    """Raise a clear error when the interpreter is older than the baseline."""
    if sys.version_info < MINIMUM_PYTHON:
        required = ".".join(str(part) for part in MINIMUM_PYTHON)
        actual = ".".join(str(part) for part in sys.version_info[:3])
        raise RuntimeError(
            f"Machine-Soul requires Python {required} or newer; running {actual}."
        )
