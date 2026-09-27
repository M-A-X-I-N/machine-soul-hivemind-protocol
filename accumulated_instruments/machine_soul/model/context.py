"""Resolved operation-wide runtime context."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .application import Platform


class ConflictPolicy(str, Enum):
    """How a mutating operation handles existing unmanaged state."""

    PROMPT = "prompt"
    ABORT = "abort"
    BACKUP_AND_REPLACE = "backup_and_replace"


@dataclass(frozen=True)
class TargetAccount:
    """Logical account targeted by an operation, independent of execution identity."""

    name: str
    home: Path
    is_current: bool
    local_app_data: Path | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Target account name cannot be empty.")
        object.__setattr__(self, "home", Path(self.home))
        if self.local_app_data is not None:
            object.__setattr__(self, "local_app_data", Path(self.local_app_data))


@dataclass(frozen=True)
class OperationContext:
    """Fully resolved common inputs passed to shared operation engines."""

    repository_root: Path
    platform: Platform
    host: str
    target_account: TargetAccount
    dry_run: bool = False
    conflict_policy: ConflictPolicy = ConflictPolicy.ABORT
    environment: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        root = Path(self.repository_root)
        if not self.host.strip():
            raise ValueError("Host identity cannot be empty.")
        if not isinstance(self.platform, Platform):
            raise TypeError("platform must be a Platform.")
        if not isinstance(self.target_account, TargetAccount):
            raise TypeError("target_account must be a TargetAccount.")
        if not isinstance(self.conflict_policy, ConflictPolicy):
            raise TypeError("conflict_policy must be a ConflictPolicy.")
        object.__setattr__(self, "repository_root", root)
        object.__setattr__(self, "environment", MappingProxyType(dict(self.environment)))
