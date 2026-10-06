"""Oh My Posh theme usability and consumer-selection verification."""

from __future__ import annotations

import ntpath
import os
from pathlib import Path
import shutil

from .configuration import ConfigurationResolutionError, resolve_source
from .model import (
    Application,
    EvidenceStrength,
    OhMyPoshVerification,
    OperationContext,
    Platform,
    PlatformDeclaration,
    VerificationConclusion,
    VerificationObservation,
)
from .process import ProcessResult, run_process


_MARKER = "__MSHP_POSH_THEME__="


def _configuration(declaration: PlatformDeclaration, name: str):
    matches = [item for item in declaration.configurations if item.name == name]
    if len(matches) != 1:
        raise ConfigurationResolutionError(
            f"Verification configuration {name!r} is not uniquely declared."
        )
    return matches[0]


def _theme_probe_failure(stderr: str, stdout: str) -> VerificationConclusion:
    text = (stderr + "\n" + stdout).casefold()
    config_terms = (
        "invalid",
        "parse",
        "json",
        "yaml",
        "config",
        "failed to load",
        "failed loading",
        "error loading",
    )
    if any(term in text for term in config_terms):
        return VerificationConclusion.NOT_EFFECTIVE
    return VerificationConclusion.INDETERMINATE


def _application_probe(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: OhMyPoshVerification,
) -> tuple[Path | None, VerificationObservation]:
    configuration = _configuration(declaration, strategy.configuration_name)
    try:
        source = resolve_source(context, application, configuration)
    except ConfigurationResolutionError as exc:
        return None, VerificationObservation(
            "omp_theme_probe",
            "oh_my_posh",
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {
                "configuration": strategy.configuration_name,
                "reason": str(exc),
            },
        )

    executable = shutil.which(
        strategy.executable_name,
        path=context.environment.get("PATH"),
    )
    if executable is None:
        return source, VerificationObservation(
            "omp_theme_probe",
            "oh_my_posh",
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {
                "theme": str(source),
                "reason": f"Executable {strategy.executable_name!r} is unavailable.",
            },
        )

    argv = [
        executable,
        "print",
        "primary",
        "--config",
        str(source),
        "--shell",
        "uni",
    ]
    result = run_process(argv, timeout=15, environ=context.environment)
    supports = (
        VerificationConclusion.EFFECTIVE
        if result.returncode == 0
        else _theme_probe_failure(result.stderr, result.stdout)
    )
    data: dict[str, object] = {
        "theme": str(source),
        "executable": executable,
        "argv": argv,
        "returncode": result.returncode,
    }
    if result.returncode != 0:
        data["stderr"] = result.stderr[-2000:]
        data["stdout"] = result.stdout[-2000:]

    return source, VerificationObservation(
        "omp_theme_probe",
        "oh_my_posh",
        EvidenceStrength.APPLICATION,
        supports,
        data,
    )


def _consumer_argv(consumer: str, executable: str) -> list[str]:
    if consumer == "bash":
        return [
            executable,
            "--noprofile",
            "-i",
            "-c",
            f'printf "{_MARKER}%s\\n" "${{POSH_THEME-}}"',
        ]
    if consumer == "zsh":
        return [
            executable,
            "-i",
            "-c",
            f'printf "{_MARKER}%s\\n" "${{POSH_THEME-}}"',
        ]
    if consumer == "fish":
        return [
            executable,
            "-i",
            "-c",
            f'printf "{_MARKER}%s\\n" "$POSH_THEME"',
        ]
    if consumer == "powershell":
        return [
            executable,
            "-Command",
            f"[Console]::Out.Write('{_MARKER}' + $env:POSH_THEME)",
        ]
    raise ValueError(f"Unsupported Oh My Posh consumer: {consumer!r}.")


def _consumer_executable(consumer: str) -> str:
    if consumer == "powershell":
        return "powershell.exe"
    return consumer


def _selected_theme(output: str) -> str | None:
    selected = None
    for line in output.splitlines():
        index = line.find(_MARKER)
        if index < 0:
            continue
        value = line[index + len(_MARKER):].strip()
        selected = value or None
    return selected


def _windows_theme_path(
    selected: str,
    context: OperationContext,
) -> str:
    if not selected.startswith("/"):
        return selected
    cygpath = shutil.which("cygpath", path=context.environment.get("PATH"))
    if cygpath is None:
        return selected
    result = run_process(
        [cygpath, "-w", selected],
        timeout=10,
        environ=context.environment,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().splitlines()[0]
    return selected


def _same_theme(
    selected: str,
    expected: Path,
    context: OperationContext,
) -> bool:
    if context.platform is Platform.WINDOWS:
        selected = _windows_theme_path(selected, context)
        return ntpath.normcase(ntpath.normpath(selected)) == ntpath.normcase(
            ntpath.normpath(str(expected))
        )
    return os.path.normcase(os.path.realpath(selected)) == os.path.normcase(
        os.path.realpath(expected)
    )


def _consumer_observation(
    consumer: str,
    expected: Path,
    context: OperationContext,
) -> VerificationObservation | None:
    executable_name = _consumer_executable(consumer)
    executable = shutil.which(
        executable_name,
        path=context.environment.get("PATH"),
    )
    if executable is None:
        return None

    environ = dict(context.environment)
    environ["MACHINE_SOUL"] = str(context.repository_root)
    environ["MACHINE_SOUL_HOST"] = context.host
    environ["MACHINE_SOUL_ACCOUNT"] = context.target_account.name
    if context.platform is Platform.LINUX:
        environ["HOME"] = str(context.target_account.home)
        environ["HISTFILE"] = os.devnull

    result = run_process(
        _consumer_argv(consumer, executable),
        timeout=15,
        environ=environ,
    )
    if result.returncode != 0:
        return VerificationObservation(
            "omp_consumer_selection",
            consumer,
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {
                "consumer": consumer,
                "executable": executable,
                "expected_theme": str(expected),
                "reason": "Controlled consumer startup returned nonzero.",
                "returncode": result.returncode,
                "stderr": result.stderr[-2000:],
            },
        )

    selected = _selected_theme(result.stdout + "\n" + result.stderr)
    if selected is None:
        return VerificationObservation(
            "omp_consumer_selection",
            consumer,
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {
                "consumer": consumer,
                "executable": executable,
                "expected_theme": str(expected),
                "reason": "Consumer started but did not expose POSH_THEME.",
            },
        )

    matches = _same_theme(selected, expected, context)
    return VerificationObservation(
        "omp_consumer_selection",
        consumer,
        EvidenceStrength.RUNTIME,
        (
            VerificationConclusion.EFFECTIVE
            if matches
            else VerificationConclusion.NOT_EFFECTIVE
        ),
        {
            "consumer": consumer,
            "executable": executable,
            "selected_theme": selected,
            "expected_theme": str(expected),
            "matches": matches,
        },
    )


def verify_oh_my_posh(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: OhMyPoshVerification,
) -> tuple[VerificationObservation, ...]:
    """Return separate theme-usability and consumer-selection observations."""
    source, application_observation = _application_probe(
        application,
        declaration,
        context,
        strategy,
    )
    observations = [application_observation]

    if source is None or not context.target_account.is_current:
        return tuple(observations)

    for consumer in strategy.consumers:
        observation = _consumer_observation(
            consumer,
            source,
            context,
        )
        if observation is not None:
            observations.append(observation)

    return tuple(observations)
