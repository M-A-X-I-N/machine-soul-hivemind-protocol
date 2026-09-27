"""Canonical configuration source/destination resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import Application, ConfigurationFile, HomeRelativeDestination, OperationContext, PlatformDeclaration


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
    base = context.repository_root / "assimilation_directives" / application.id
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
    strategy = configuration.destination
    if isinstance(strategy, HomeRelativeDestination):
        return context.target_account.home / strategy.relative_path

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
