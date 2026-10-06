"""Side-effect-free models for Windows native toolchain discovery and ownership."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


_ARCH_ALIASES = {
    "x86": "x86",
    "x64": "amd64",
    "amd64": "amd64",
    "arm": "arm",
    "arm64": "arm64",
    "arm64ec": "arm64ec",
}


def normalize_native_architecture(value: str) -> str:
    """Normalize common Visual Studio/native architecture spellings."""
    normalized = value.strip().casefold()
    try:
        return _ARCH_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported native architecture: {value!r}.") from exc


@dataclass(frozen=True)
class VisualStudioInstance:
    """One exact Visual Studio Setup instance and its observed native capabilities."""

    instance_id: str
    installation_path: Path
    installation_version: str
    product_id: str | None = None
    display_name: str | None = None
    channel_id: str | None = None
    is_complete: bool = False
    is_launchable: bool = False
    is_prerelease: bool = False
    component_ids: frozenset[str] = field(default_factory=frozenset)
    msvc_versions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.instance_id.strip():
            raise ValueError("Visual Studio instance ID cannot be empty.")
        if not self.installation_version.strip():
            raise ValueError("Visual Studio installation version cannot be empty.")
        object.__setattr__(self, "installation_path", Path(self.installation_path))
        object.__setattr__(
            self,
            "component_ids",
            frozenset(str(item) for item in self.component_ids if str(item).strip()),
        )
        object.__setattr__(
            self,
            "msvc_versions",
            tuple(sorted({str(item) for item in self.msvc_versions if str(item).strip()})),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "instance_id": self.instance_id,
            "installation_path": str(self.installation_path),
            "installation_version": self.installation_version,
            "product_id": self.product_id,
            "display_name": self.display_name,
            "channel_id": self.channel_id,
            "is_complete": self.is_complete,
            "is_launchable": self.is_launchable,
            "is_prerelease": self.is_prerelease,
            "component_ids": sorted(self.component_ids),
            "msvc_versions": list(self.msvc_versions),
        }


@dataclass(frozen=True)
class NativeToolchainRequirement:
    """Machine capability constraint for one Windows native build session."""

    required_components: frozenset[str] = field(default_factory=frozenset)
    msvc_version_prefix: str | None = None
    windows_sdk_component: str | None = None
    host_architecture: str = "amd64"
    target_architecture: str = "amd64"
    allow_prerelease: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_components",
            frozenset(str(item) for item in self.required_components if str(item).strip()),
        )
        object.__setattr__(
            self,
            "host_architecture",
            normalize_native_architecture(self.host_architecture),
        )
        object.__setattr__(
            self,
            "target_architecture",
            normalize_native_architecture(self.target_architecture),
        )
        if self.msvc_version_prefix is not None and not self.msvc_version_prefix.strip():
            raise ValueError("msvc_version_prefix cannot be empty.")
        if self.windows_sdk_component is not None and not self.windows_sdk_component.strip():
            raise ValueError("windows_sdk_component cannot be empty.")

    @property
    def component_ids(self) -> frozenset[str]:
        components = set(self.required_components)
        if self.windows_sdk_component is not None:
            components.add(self.windows_sdk_component)
        return frozenset(components)

    def to_dict(self) -> dict[str, object]:
        return {
            "required_components": sorted(self.required_components),
            "msvc_version_prefix": self.msvc_version_prefix,
            "windows_sdk_component": self.windows_sdk_component,
            "host_architecture": self.host_architecture,
            "target_architecture": self.target_architecture,
            "allow_prerelease": self.allow_prerelease,
        }


@dataclass(frozen=True)
class NativeToolchainOwnership:
    """Machine-scoped ownership of exact components inside an adopted setup instance."""

    host: str
    instance_id: str
    installation_path: Path
    owned_components: frozenset[str] = field(default_factory=frozenset)
    schema: int = 1

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("Native toolchain ownership requires a host.")
        if not self.instance_id.strip():
            raise ValueError("Native toolchain ownership requires an instance ID.")
        object.__setattr__(self, "installation_path", Path(self.installation_path))
        object.__setattr__(
            self,
            "owned_components",
            frozenset(str(item) for item in self.owned_components if str(item).strip()),
        )

    def with_owned_components(
        self,
        components: Iterable[str],
    ) -> "NativeToolchainOwnership":
        return NativeToolchainOwnership(
            host=self.host,
            instance_id=self.instance_id,
            installation_path=self.installation_path,
            owned_components=frozenset(components),
            schema=self.schema,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "host": self.host,
            "instance_id": self.instance_id,
            "installation_path": str(self.installation_path),
            "owned_components": sorted(self.owned_components),
        }
