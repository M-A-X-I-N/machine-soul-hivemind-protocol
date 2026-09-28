"""Safe shared subprocess invocation."""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


def run_process(
    argv: Sequence[str],
    *,
    timeout: float | None = None,
    environ: Mapping[str, str] | None = None,
) -> ProcessResult:
    """Run argv directly without shell interpolation and capture text streams."""
    if not argv:
        raise ValueError("argv cannot be empty.")
    completed = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
        check=False,
        env=(dict(environ) if environ is not None else None),
    )
    return ProcessResult(completed.returncode, completed.stdout, completed.stderr)
