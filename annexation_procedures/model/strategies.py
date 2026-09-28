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
class InstallationDiscoveryStrategy(Protocol):
    """Marker protocol for declared read-only installation discovery strategies."""


@runtime_checkable
class DestinationStrategy(Protocol):
    """Marker protocol for declared configuration destination strategies."""


@runtime_checkable
class ConfigurationStrategy(Protocol):
    """Marker protocol for declared whole-configuration strategies."""


@dataclass(frozen=True)
class InstallationDiscoveryPlan:
    """Ordered read-only probes used to assess existing installations."""

    strategies: tuple[InstallationDiscoveryStrategy, ...]

    def __post_init__(self) -> None:
        if not self.strategies:
            raise ValueError("Installation discovery plan requires at least one strategy.")


@dataclass(frozen=True)
class DpkgPackageDiscovery:
    package_name: str
    executable_name: str | None = None
    preferred: bool = False


@dataclass(frozen=True)
class WingetPackageDiscovery:
    package_id: str
    source: str = "winget"
    preferred: bool = False
    executable_name: str | None = None
    version_arguments: tuple[str, ...] = ()
    package_family_name: str | None = None


@dataclass(frozen=True)
class WindowsArpDiscovery:
    display_name: str | None = None
    publisher: str | None = None
    product_code: str | None = None
    executable_name: str | None = None
    preferred: bool = False

    def __post_init__(self) -> None:
        if not any((self.display_name, self.product_code, self.executable_name)):
            raise ValueError("ARP discovery requires an exact identity or executable correlation.")


@dataclass(frozen=True)
class WindowsAppxDiscovery:
    package_family_name: str
    executable_name: str | None = None
    preferred: bool = False


@dataclass(frozen=True)
class BuiltInExecutableDiscovery:
    executable_name: str
    identity: str
    version_arguments: tuple[str, ...] = ()


@dataclass(frozen=True)
class WindowsPosixPackageDiscovery:
    package_name: str
    executable_name: str
    version_arguments: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutableDiscovery:
    executable_name: str
    version_arguments: tuple[str, ...] = ()
    preferred: bool = False


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


@dataclass(frozen=True)
class LocalAppDataRelativeDestination:
    """Destination relative to the logical target account LocalAppData root."""

    relative_path: str

    def __post_init__(self) -> None:
        if not self.relative_path or self.relative_path.startswith(("/", "\\")):
            raise ValueError("LocalAppData destination must be a non-empty relative path.")


@dataclass(frozen=True)
class WindowsTerminalSettingsDestination:
    """Select packaged or unpackaged Windows Terminal settings."""


@dataclass(frozen=True)
class PowerShellProfileDestination:
    """Resolve the current target account's PowerShell CurrentUserCurrentHost profile."""

    executable: str = "powershell.exe"


@dataclass(frozen=True)
class WindowsPosixHomeDestination:
    """Destination relative to the compatibility shell's HOME."""

    relative_path: str

    def __post_init__(self) -> None:
        if not self.relative_path or self.relative_path.startswith(("/", "\\")):
            raise ValueError("POSIX-home destination must be a non-empty relative path.")


@dataclass(frozen=True)
class CustomConfiguration:
    """Escape hatch for genuinely application-specific config orchestration."""

    handler: Callable[..., object]
