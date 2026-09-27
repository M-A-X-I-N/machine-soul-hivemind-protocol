"""Declarative application schema."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Mapping

from .strategies import ConfigurationStrategy, DestinationStrategy, InstallationStrategy


_APPLICATION_ID = re.compile(r"^[a-z][a-z0-9_]*$")


class Platform(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"


class Operation(str, Enum):
    APPLY_CONFIG = "apply_config"
    UNAPPLY_CONFIG = "unapply_config"
    CHECK_CONFIG = "check_config"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    CHECK_INSTALLED = "check_installed"


class Support(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    NOT_IMPLEMENTED = "not_implemented"


@dataclass(frozen=True)
class ConfigurationFile:
    """One canonical config leaf and its native destination strategy."""

    name: str
    source_leaf: str
    destination: DestinationStrategy

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Configuration name cannot be empty.")
        if not self.source_leaf or "/" in self.source_leaf or "\\" in self.source_leaf:
            raise ValueError("source_leaf must be one filename, not a path.")


@dataclass(frozen=True)
class PlatformDeclaration:
    """Declarative application behavior for one platform."""

    platform: Platform
    capabilities: Mapping[Operation, Support]
    configurations: tuple[ConfigurationFile, ...] = ()
    install_strategy: InstallationStrategy | None = None
    configuration_strategy: ConfigurationStrategy | None = None

    def __post_init__(self) -> None:
        caps = dict(self.capabilities)
        object.__setattr__(self, "capabilities", caps)

        if caps.get(Operation.INSTALL) is Support.SUPPORTED and self.install_strategy is None:
            raise ValueError("Supported install operation requires an install strategy.")

        names = [config.name for config in self.configurations]
        if len(names) != len(set(names)):
            raise ValueError("Configuration names must be unique within a platform declaration.")

    def support_for(self, operation: Operation) -> Support:
        return self.capabilities.get(operation, Support.UNSUPPORTED)


@dataclass(frozen=True)
class Application:
    """Side-effect-free declaration imported from an app's _application.py."""

    id: str
    display_name: str
    platforms: tuple[PlatformDeclaration, ...]

    def __post_init__(self) -> None:
        if not _APPLICATION_ID.fullmatch(self.id):
            raise ValueError("Application id must use repository snake_case.")
        if not self.display_name.strip():
            raise ValueError("Application display_name cannot be empty.")

        platform_ids = [entry.platform for entry in self.platforms]
        if len(platform_ids) != len(set(platform_ids)):
            raise ValueError("An application may declare each platform only once.")

    def for_platform(self, platform: Platform) -> PlatformDeclaration | None:
        for declaration in self.platforms:
            if declaration.platform is platform:
                return declaration
        return None
