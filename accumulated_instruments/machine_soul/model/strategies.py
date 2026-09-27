"""Declarative strategy/value types.

These classes contain no installation or configuration behavior. Shared
operation engines interpret them later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class InstallationStrategy(Protocol):
    """Marker protocol for declared installation strategies."""


@runtime_checkable
class DestinationStrategy(Protocol):
    """Marker protocol for declared configuration destination strategies."""


@dataclass(frozen=True)
class WingetPackage:
    package_id: str
    source: str = "winget"


@dataclass(frozen=True)
class AptPackage:
    package_name: str


@dataclass(frozen=True)
class RemoteInstallScript:
    url: str
    interpreter: str = "sh"
    arguments: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandaloneBinary:
    url: str
    executable_name: str


@dataclass(frozen=True)
class CustomInstaller:
    """Escape hatch for genuinely application-specific installation logic."""

    handler: Callable[..., object]


@dataclass(frozen=True)
class HomeRelativeDestination:
    """Destination path resolved relative to the logical target account home."""

    relative_path: str

    def __post_init__(self) -> None:
        if not self.relative_path or self.relative_path.startswith(("/", "\\")):
            raise ValueError("Home-relative destination must be a non-empty relative path.")
