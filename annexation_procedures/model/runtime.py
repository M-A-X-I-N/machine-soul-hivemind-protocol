"""Side-effect-free models and backend protocol for runtime annexation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable

from .context import OperationContext
from .result import OperationResult


@dataclass(frozen=True)
class RuntimeSpec:
    """One exact desired runtime instance understood by a concrete backend."""

    subject: str
    version: str
    backend: str
    backend_key: str
    architecture: str | None = None
    flavor: str | None = None
    distribution: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("subject", "version", "backend", "backend_key"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "version": self.version,
            "backend": self.backend,
            "backend_key": self.backend_key,
            "architecture": self.architecture,
            "flavor": self.flavor,
            "distribution": self.distribution,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RuntimeInstance:
    """One exact observed runtime instance, independent of PATH precedence."""

    subject: str
    version: str
    backend: str
    backend_key: str
    architecture: str | None = None
    flavor: str | None = None
    distribution: str | None = None
    executable: Path | None = None
    prefix: Path | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("subject", "version", "backend", "backend_key"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")
        if self.executable is not None:
            object.__setattr__(self, "executable", Path(self.executable))
        if self.prefix is not None:
            object.__setattr__(self, "prefix", Path(self.prefix))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "version": self.version,
            "backend": self.backend,
            "backend_key": self.backend_key,
            "architecture": self.architecture,
            "flavor": self.flavor,
            "distribution": self.distribution,
            "executable": str(self.executable) if self.executable is not None else None,
            "prefix": str(self.prefix) if self.prefix is not None else None,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RuntimeDesiredState:
    """Desired runtime set plus selected/default state for one backend."""

    subject: str
    backend: str
    instances: tuple[RuntimeSpec, ...]
    selected_key: str | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject cannot be empty.")
        if not self.backend.strip():
            raise ValueError("backend cannot be empty.")

        keys: set[str] = set()
        for item in self.instances:
            if item.subject != self.subject:
                raise ValueError("All desired runtime specs must share the desired subject.")
            if item.backend != self.backend:
                raise ValueError("All desired runtime specs must share the desired backend.")
            if item.backend_key in keys:
                raise ValueError(f"Duplicate desired runtime backend key: {item.backend_key!r}.")
            keys.add(item.backend_key)

        if self.selected_key is not None and self.selected_key not in keys:
            raise ValueError("selected_key must identify one desired runtime instance.")

    @property
    def desired_keys(self) -> frozenset[str]:
        return frozenset(item.backend_key for item in self.instances)

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "backend": self.backend,
            "instances": [item.to_dict() for item in self.instances],
            "selected_key": self.selected_key,
        }


@dataclass(frozen=True)
class RuntimeOwnership:
    """Machine-scoped provenance for one exact runtime instance."""

    host: str
    subject: str
    backend: str
    backend_key: str
    version: str
    architecture: str | None = None
    flavor: str | None = None
    distribution: str | None = None
    executable: Path | None = None
    prefix: Path | None = None
    schema: int = 1

    def __post_init__(self) -> None:
        for name in ("host", "subject", "backend", "backend_key", "version"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")
        if self.executable is not None:
            object.__setattr__(self, "executable", Path(self.executable))
        if self.prefix is not None:
            object.__setattr__(self, "prefix", Path(self.prefix))

    @classmethod
    def from_instance(cls, host: str, instance: RuntimeInstance) -> "RuntimeOwnership":
        return cls(
            host=host,
            subject=instance.subject,
            backend=instance.backend,
            backend_key=instance.backend_key,
            version=instance.version,
            architecture=instance.architecture,
            flavor=instance.flavor,
            distribution=instance.distribution,
            executable=instance.executable,
            prefix=instance.prefix,
        )

    def matches_instance(self, instance: RuntimeInstance) -> bool:
        return (
            self.subject == instance.subject
            and self.backend == instance.backend
            and self.backend_key == instance.backend_key
            and self.version == instance.version
            and self.architecture == instance.architecture
            and self.flavor == instance.flavor
            and self.distribution == instance.distribution
            and self.executable == instance.executable
            and self.prefix == instance.prefix
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "host": self.host,
            "subject": self.subject,
            "backend": self.backend,
            "backend_key": self.backend_key,
            "version": self.version,
            "architecture": self.architecture,
            "flavor": self.flavor,
            "distribution": self.distribution,
            "executable": str(self.executable) if self.executable is not None else None,
            "prefix": str(self.prefix) if self.prefix is not None else None,
        }


@runtime_checkable
class RuntimeBackend(Protocol):
    """Concrete runtime lifecycle contract consumed by the shared reconciler."""

    subject: str
    name: str

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        """Discover relevant runtime instances without mutating state."""
        ...

    def selected_key(self, context: OperationContext) -> str | None:
        """Return exact backend key currently selected/default, if any."""
        ...

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        """Install one exact desired runtime instance."""
        ...

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        """Remove one exact runtime instance."""
        ...

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        """Select one exact runtime as the global/backend default."""
        ...
