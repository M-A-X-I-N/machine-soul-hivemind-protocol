"""Read-only native application configuration verification."""

from __future__ import annotations

from pathlib import Path
import shutil

from .configuration import ConfigurationResolutionError, resolve_destination
from .model import (
    Application,
    ApplicationConfigProbe,
    CmdAutoRunVerification,
    EvidenceStrength,
    OperationContext,
    PlatformDeclaration,
    ResolvedPathVerification,
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


def _resolved_path_observation(
    kind: str,
    source: str,
    destination: Path,
    *,
    executable: str | None = None,
    supports: VerificationConclusion,
    reason: str | None = None,
    evidence: EvidenceStrength = EvidenceStrength.RESOLUTION,
    extra: dict[str, object] | None = None,
) -> VerificationObservation:
    data: dict[str, object] = {
        "destination": str(destination),
        "destination_exists": destination.exists() or destination.is_symlink(),
    }
    if executable:
        data["executable"] = executable
    if reason:
        data["reason"] = reason
    if extra:
        data.update(extra)
    return VerificationObservation(kind, source, evidence, supports, data)


def verify_resolved_path(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: ResolvedPathVerification,
) -> VerificationObservation:
    configuration = _configuration(declaration, strategy.configuration_name)
    try:
        destination = resolve_destination(context, configuration)
    except ConfigurationResolutionError as exc:
        return VerificationObservation(
            "resolved_configuration_path",
            application.id,
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {"reason": str(exc), "configuration": strategy.configuration_name},
        )

    executable = None
    if strategy.executable_name:
        executable = shutil.which(
            strategy.executable_name,
            path=context.environment.get("PATH"),
        )
        if executable is None:
            return _resolved_path_observation(
                "resolved_configuration_path",
                application.id,
                destination,
                supports=VerificationConclusion.INDETERMINATE,
                reason=f"Executable {strategy.executable_name!r} is unavailable.",
            )

    exists = destination.exists() or destination.is_symlink()
    return _resolved_path_observation(
        "resolved_configuration_path",
        application.id,
        destination,
        executable=executable,
        supports=(
            VerificationConclusion.EFFECTIVE
            if exists
            else VerificationConclusion.NOT_EFFECTIVE
        ),
    )


def verify_application_config_probe(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: ApplicationConfigProbe,
) -> VerificationObservation:
    configuration = _configuration(declaration, strategy.configuration_name)
    try:
        destination = resolve_destination(context, configuration)
    except ConfigurationResolutionError as exc:
        return VerificationObservation(
            "application_config_probe",
            application.id,
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {"reason": str(exc), "configuration": strategy.configuration_name},
        )

    executable = shutil.which(
        strategy.executable_name,
        path=context.environment.get("PATH"),
    )
    if executable is None:
        return _resolved_path_observation(
            "application_config_probe",
            application.id,
            destination,
            supports=VerificationConclusion.INDETERMINATE,
            reason=f"Executable {strategy.executable_name!r} is unavailable.",
        )

    if not (destination.exists() or destination.is_symlink()):
        return _resolved_path_observation(
            "application_config_probe",
            application.id,
            destination,
            executable=executable,
            supports=VerificationConclusion.NOT_EFFECTIVE,
            reason="The application-native config path does not exist.",
        )

    result = run_process(
        [executable, *strategy.arguments],
        timeout=15,
        environ=context.environment,
    )
    if result.returncode != 0:
        return _resolved_path_observation(
            "application_config_probe",
            application.id,
            destination,
            executable=executable,
            supports=VerificationConclusion.INDETERMINATE,
            reason="Application-native config probe returned nonzero.",
            evidence=EvidenceStrength.APPLICATION,
            extra={
                "argv": [executable, *strategy.arguments],
                "returncode": result.returncode,
                "stderr": result.stderr[-2000:],
            },
        )

    return _resolved_path_observation(
        "application_config_probe",
        application.id,
        destination,
        executable=executable,
        supports=VerificationConclusion.EFFECTIVE,
        evidence=EvidenceStrength.APPLICATION,
        extra={
            "argv": [executable, *strategy.arguments],
            "stdout": result.stdout[-2000:],
        },
    )


def _cmd_registry_subkey(context: OperationContext) -> str:
    override = context.environment.get("MACHINE_SOUL_CMD_REGISTRY_KEY")
    if not override:
        return r"Software\Microsoft\Command Processor"
    prefix = "HKCU:\\"
    if not override.upper().startswith(prefix.upper()):
        raise ValueError("CMD registry override must target HKCU.")
    return override[len(prefix):].replace("/", "\\")


def _read_cmd_autorun(context: OperationContext) -> str | None:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _cmd_registry_subkey(context)) as key:
            value, _ = winreg.QueryValueEx(key, "AutoRun")
            return str(value)
    except FileNotFoundError:
        return None


def verify_cmd_autorun(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    strategy: CmdAutoRunVerification,
) -> VerificationObservation:
    configuration = _configuration(declaration, strategy.configuration_name)
    try:
        destination = resolve_destination(context, configuration)
        current = _read_cmd_autorun(context)
    except (ConfigurationResolutionError, OSError, ValueError) as exc:
        return VerificationObservation(
            "cmd_autorun_resolution",
            "cmd",
            EvidenceStrength.RESOLUTION,
            VerificationConclusion.INDETERMINATE,
            {"reason": str(exc)},
        )

    expected = f'call "{destination}"'
    matches = current == expected
    exists = destination.exists() or destination.is_symlink()
    return _resolved_path_observation(
        "cmd_autorun_resolution",
        "cmd",
        destination,
        supports=(
            VerificationConclusion.EFFECTIVE
            if matches and exists
            else VerificationConclusion.NOT_EFFECTIVE
        ),
        extra={
            "current_autorun": current,
            "expected_autorun": expected,
            "autorun_matches": matches,
        },
    )
