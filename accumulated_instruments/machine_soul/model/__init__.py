"""Side-effect-free declaration/value models used by Machine-Soul."""

from .application import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
)
from .strategies import (
    AptPackage,
    CustomInstaller,
    HomeRelativeDestination,
    RemoteInstallScript,
    StandaloneBinary,
    WingetPackage,
)

__all__ = [
    "Application",
    "ConfigurationFile",
    "Operation",
    "Platform",
    "PlatformDeclaration",
    "Support",
    "AptPackage",
    "CustomInstaller",
    "HomeRelativeDestination",
    "RemoteInstallScript",
    "StandaloneBinary",
    "WingetPackage",
]
