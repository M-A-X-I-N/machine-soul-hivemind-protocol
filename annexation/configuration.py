"""Canonical configuration source/destination resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .model import (
    Application,
    ConfigurationFile,
    HomeRelativeDestination,
    LocalAppDataRelativeDestination,
    OperationContext,
    PlatformDeclaration,
    PowerShellProfileDestination,
    WindowsPosixHomeDestination,
    WindowsTerminalSettingsDestination,
)
from .process import run_process


class ConfigurationResolutionError(RuntimeError):
    """A declared configuration cannot be resolved for the requested context."""


@dataclass(frozen=True)
class ResolvedConfiguration:
    configuration: ConfigurationFile
    source: Path
    destination: Path


def source_candidates(
    context: OperationContext,
    application: Application,
    configuration: ConfigurationFile,
) -> tuple[Path, ...]:
    """Return canonical source candidates in documented specificity order."""
    base = context.repository_root / "assimilation" / application.id
    host = context.host
    account = context.target_account.name
    leaf = configuration.source_leaf
    return (
        base / "hosts" / host / "users" / account / leaf,
        base / "hosts" / host / "common" / leaf,
        base / "default" / "users" / account / leaf,
        base / "default" / "common" / leaf,
    )


def resolve_source(
    context: OperationContext,
    application: Application,
    configuration: ConfigurationFile,
) -> Path:
    """Resolve one complete tracked source file using shared precedence."""
    for candidate in source_candidates(context, application, configuration):
        if candidate.is_file():
            return candidate
    raise ConfigurationResolutionError(
        f"No canonical source for {application.id}/{configuration.name} "
        f"on host={context.host!r}, account={context.target_account.name!r}."
    )


def resolve_destination(
    context: OperationContext,
    configuration: ConfigurationFile,
) -> Path:
    """Resolve the native destination selected by a declarative strategy."""
    override = context.environment.get("MACHINE_SOUL_CONFIG_DESTINATION")
    if override:
        return Path(override)

    strategy = configuration.destination
    if isinstance(strategy, HomeRelativeDestination):
        return context.target_account.home / strategy.relative_path

    if isinstance(strategy, LocalAppDataRelativeDestination):
        root = context.target_account.local_app_data
        if root is None:
            raise ConfigurationResolutionError(
                "Target account has no resolved LocalAppData root."
            )
        return root / strategy.relative_path

    if isinstance(strategy, WindowsTerminalSettingsDestination):
        root = context.target_account.local_app_data
        if root is None:
            raise ConfigurationResolutionError(
                "Target account has no resolved LocalAppData root."
            )
        packaged_dir = (
            root
            / "Packages"
            / "Microsoft.WindowsTerminal_8wekyb3d8bbwe"
            / "LocalState"
        )
        if packaged_dir.is_dir():
            return packaged_dir / "settings.json"
        return root / "Microsoft" / "Windows Terminal" / "settings.json"

    if isinstance(strategy, PowerShellProfileDestination):
        executable = shutil.which(strategy.executable, path=context.environment.get("PATH"))
        if executable is None:
            raise ConfigurationResolutionError(
                f"PowerShell executable {strategy.executable!r} is unavailable."
            )
        result = run_process(
            [
                executable,
                "-NoProfile",
                "-Command",
                "[Console]::Out.Write($PROFILE.CurrentUserCurrentHost)",
            ],
            environ=context.environment,
        )
        if result.returncode != 0 or not result.stdout.strip():
            raise ConfigurationResolutionError(
                "PowerShell profile destination could not be resolved."
            )
        return Path(result.stdout.strip())

    if isinstance(strategy, WindowsPosixHomeDestination):
        home = context.environment.get("HOME")
        if not home:
            raise ConfigurationResolutionError(
                "Windows POSIX destination requires HOME from the compatibility environment."
            )
        cygpath = shutil.which("cygpath", path=context.environment.get("PATH"))
        if cygpath is None:
            raise ConfigurationResolutionError(
                "Windows POSIX destination requires cygpath."
            )
        raw = home.rstrip("/\\") + "/" + strategy.relative_path.replace("\\", "/")
        result = run_process([cygpath, "-w", raw], environ=context.environment)
        if result.returncode != 0 or not result.stdout.strip():
            raise ConfigurationResolutionError(
                "cygpath failed to translate the POSIX-shell destination."
            )
        return Path(result.stdout.strip())

    raise ConfigurationResolutionError(
        f"Unsupported destination strategy type: {type(strategy).__name__}."
    )


def resolve_configurations(
    context: OperationContext,
    application: Application,
    declaration: PlatformDeclaration,
) -> tuple[ResolvedConfiguration, ...]:
    """Resolve every declared config target for one application/platform."""
    resolved = []
    for configuration in declaration.configurations:
        resolved.append(
            ResolvedConfiguration(
                configuration,
                resolve_source(context, application, configuration),
                resolve_destination(context, configuration),
            )
        )
    return tuple(resolved)
