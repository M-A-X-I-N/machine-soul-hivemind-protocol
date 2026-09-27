"""Side-effect-free declaration/value models used by Machine-Soul."""

from .application import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
)
from .result import OperationResult, ResultStatus
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
    "OperationResult",
    "ResultStatus",
    "AptPackage",
    "CustomInstaller",
    "HomeRelativeDestination",
    "RemoteInstallScript",
    "StandaloneBinary",
    "WingetPackage",
]
