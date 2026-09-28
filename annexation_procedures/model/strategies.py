"""Declarative strategy/value types.

These classes contain no installation or configuration behavior. Shared
operation engines interpret them later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol, runtime_checkable

from .discovery import InstallationScope
from .installation_scope import InstallationScopePolicy


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


@runtime_checkable
class ConfigurationVerificationStrategy(Protocol):
    """Marker protocol for declared read-only config verification strategies."""


@dataclass(frozen=True)
class ConfigurationVerificationPlan:
    """Ordered read-only probes used to verify effective configuration."""

    strategies: tuple[ConfigurationVerificationStrategy, ...]

    def __post_init__(self) -> None:
        if not self.strategies:
            raise ValueError("Configuration verification plan requires at least one strategy.")


@dataclass(frozen=True)
class OhMyPoshVerification:
    """Verify OMP theme usability and consumer-shell theme selection."""

    executable_name: str
    consumers: tuple[str, ...]
    configuration_name: str = "theme"

    def __post_init__(self) -> None:
        supported = {"bash", "zsh", "fish", "powershell"}
        unknown = set(self.consumers) - supported
        if unknown:
            raise ValueError(
                f"Unsupported Oh My Posh verification consumers: {sorted(unknown)!r}."
            )


@dataclass(frozen=True)
class ResolvedPathVerification:
    """Verify that an application resolves to an existing declared config path."""

    configuration_name: str
    executable_name: str | None = None


@dataclass(frozen=True)
class ApplicationConfigProbe:
    """Run a read-only application-native config inspection command."""

    executable_name: str
    arguments: tuple[str, ...]
    configuration_name: str


@dataclass(frozen=True)
class CmdAutoRunVerification:
    """Verify CMD's documented HKCU AutoRun selection of a command file."""

    configuration_name: str = "command_file"


@dataclass(frozen=True)
class ShellStartupVerification:
    """Verify ordinary shell startup against one declared configuration."""

    shell: str
    executable_name: str
    configuration_name: str = "main"

    def __post_init__(self) -> None:
        if self.shell not in {"bash", "zsh", "fish"}:
            raise ValueError("ShellStartupVerification supports bash, zsh, or fish.")


@dataclass(frozen=True)
class CustomVerification:
    """Narrow escape hatch for a reusable or genuinely application-specific probe."""

    handler: Callable[..., object]


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
    scope_policy: InstallationScopePolicy
    source: str = "winget"


@dataclass(frozen=True)
class AptPackage:
    package_name: str
    scope_policy: InstallationScopePolicy = field(
        default_factory=lambda: InstallationScopePolicy.fixed(InstallationScope.MACHINE),
        init=False,
    )


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
