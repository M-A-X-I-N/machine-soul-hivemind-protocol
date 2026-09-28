"""Read-only shell startup verification strategies."""

from __future__ import annotations

import os
from pathlib import Path
import shutil

from .configuration import ConfigurationResolutionError, resolve_destination
from .model import (
    Application,
    EvidenceStrength,
    OperationContext,
    Platform,
    PlatformDeclaration,
    ShellStartupVerification,
    VerificationConclusion,
    VerificationObservation,
)
from .process import run_process


def _configuration(declaration: PlatformDeclaration, name: str):
    matches = [item for item in declaration.configurations if item.name == name]
    if len(matches) != 1:
        raise ConfigurationResolutionError(
            f"Verification configuration {name!r} is not uniquely declared."
        )
    return matches[0]


def _expected_shell_path(
    destination: Path,
    context: OperationContext,
) -> tuple[str | None, str | None]:
    if context.platform is Platform.LINUX:
        return str(destination), None

    cygpath = shutil.which("cygpath", path=context.environment.get("PATH"))
    if cygpath is None:
        return None, "cygpath is unavailable in the active Windows POSIX environment."
    result = run_process(
        [cygpath, "-u", str(destination)],
        timeout=10,
        environ=context.environment,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None, "cygpath could not translate the expected configuration path."
    return result.stdout.strip().splitlines()[0], None


def _contains_path(trace: str, expected: str) -> bool:
    normalized_trace = trace.replace("\\", "/").casefold()
    normalized_expected = expected.replace("\\", "/").casefold()
    return normalized_expected in normalized_trace


def _resolution_observation(
    strategy: ShellStartupVerification,
    destination: Path,
    executable: str | None,
    *,
    supports: VerificationConclusion,
    reason: str,
) -> VerificationObservation:
    data: dict[str, object] = {
        "shell": strategy.shell,
        "destination": str(destination),
        "reason": reason,
        "destination_exists": destination.exists() or destination.is_symlink(),
    }
    if executable:
        data["executable"] = executable
    return VerificationObservation(
        "shell_startup_resolution",
        strategy.shell,
        EvidenceStrength.RESOLUTION,
        supports,
        data,
    )


def verify_shell_startup(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: ShellStartupVerification,
) -> VerificationObservation:
    """Observe ordinary startup without sourcing or mutating the config."""
    configuration = _configuration(declaration, strategy.configuration_name)
    destination = resolve_destination(context, configuration)
    executable = shutil.which(
        strategy.executable_name,
        path=context.environment.get("PATH"),
    )

    if executable is None:
        return _resolution_observation(
            strategy,
            destination,
            None,
            supports=VerificationConclusion.INDETERMINATE,
            reason="Shell executable is unavailable in the target environment.",
        )

    if not context.target_account.is_current:
        return _resolution_observation(
            strategy,
            destination,
            executable,
            supports=VerificationConclusion.INDETERMINATE,
            reason="Controlled startup cannot impersonate a non-current target account.",
        )

    if strategy.shell == "fish":
        exists = destination.exists() or destination.is_symlink()
        return _resolution_observation(
            strategy,
            destination,
            executable,
            supports=(
                VerificationConclusion.EFFECTIVE
                if exists
                else VerificationConclusion.NOT_EFFECTIVE
            ),
            reason=(
                "Fish default startup resolves this config path, but native tracing "
                "does not provide a trustworthy source-path attribution contract."
            ),
        )

    expected, translation_error = _expected_shell_path(destination, context)
    if expected is None:
        return _resolution_observation(
            strategy,
            destination,
            executable,
            supports=VerificationConclusion.INDETERMINATE,
            reason=translation_error or "Expected shell path could not be resolved.",
        )

    environ = dict(context.environment)
    if context.platform is Platform.LINUX:
        environ["HOME"] = str(context.target_account.home)
        environ["HISTFILE"] = os.devnull

    if strategy.shell == "bash":
        environ["PS4"] = "+${BASH_SOURCE}:${LINENO}: "
        positive = [executable, "--noprofile", "-i", "-x", "-c", "exit"]
        negative = [executable, "--noprofile", "--norc", "-i", "-x", "-c", "exit"]
    else:
        environ["PS4"] = "+%N:%i: "
        positive = [executable, "-i", "-x", "-c", "exit"]
        negative = [executable, "-f", "-i", "-x", "-c", "exit"]

    positive_result = run_process(positive, timeout=10, environ=environ)
    negative_result = run_process(negative, timeout=10, environ=environ)
    positive_trace = positive_result.stderr + "\n" + positive_result.stdout
    negative_trace = negative_result.stderr + "\n" + negative_result.stdout

    positive_has = _contains_path(positive_trace, expected)
    negative_has = _contains_path(negative_trace, expected)
    if positive_result.returncode != 0 or negative_result.returncode != 0:
        return _resolution_observation(
            strategy,
            destination,
            executable,
            supports=VerificationConclusion.INDETERMINATE,
            reason="Controlled shell startup trace failed.",
        )

    effective = positive_has and not negative_has
    data = {
        "shell": strategy.shell,
        "executable": executable,
        "destination": str(destination),
        "expected_trace_path": expected,
        "ordinary_startup_attributed": positive_has,
        "startup_disabled_attributed": negative_has,
    }
    return VerificationObservation(
        "shell_startup_trace",
        strategy.shell,
        EvidenceStrength.RUNTIME,
        (
            VerificationConclusion.EFFECTIVE
            if effective
            else VerificationConclusion.NOT_EFFECTIVE
        ),
        data,
    )
