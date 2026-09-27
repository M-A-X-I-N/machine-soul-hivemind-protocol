"""Common semantic operation result model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import re
from types import MappingProxyType
from typing import Mapping


_RESULT_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


class ResultStatus(str, Enum):
    """Broad semantic outcome category shared by all operations."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNSUPPORTED = "unsupported"
    NOT_IMPLEMENTED = "not_implemented"
    ERROR = "error"


_EXIT_CODES = {
    ResultStatus.SUCCESS: 0,
    ResultStatus.FAILURE: 1,
    ResultStatus.UNSUPPORTED: 2,
    ResultStatus.NOT_IMPLEMENTED: 2,
    ResultStatus.ERROR: 3,
}


@dataclass(frozen=True)
class OperationResult:
    """One operation outcome independent of presentation or process transport."""

    status: ResultStatus
    changed: bool
    code: str
    message: str
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.status, ResultStatus):
            raise TypeError("status must be a ResultStatus.")
        if not isinstance(self.changed, bool):
            raise TypeError("changed must be bool.")
        if not _RESULT_CODE.fullmatch(self.code):
            raise ValueError("code must be lower_snake_case.")
        if not self.message.strip():
            raise ValueError("message cannot be empty.")

        copied = dict(self.data)
        if not all(isinstance(key, str) for key in copied):
            raise TypeError("OperationResult data keys must be strings.")

        # Machine-readable output is part of the result contract. Reject data
        # that could never cross that boundary rather than failing later in a
        # wrapper or orchestrator.
        json.dumps(copied, allow_nan=False)
        object.__setattr__(self, "data", MappingProxyType(copied))

    @property
    def exit_code(self) -> int:
        """Shared standalone-process exit code for this semantic status."""
        return _EXIT_CODES[self.status]

    def to_dict(self) -> dict[str, object]:
        """Return the canonical machine-readable semantic representation."""
        return {
            "status": self.status.value,
            "changed": self.changed,
            "code": self.code,
            "message": self.message,
            "data": dict(self.data),
        }

    @classmethod
    def success(
        cls,
        code: str,
        message: str,
        *,
        changed: bool = False,
        data: Mapping[str, object] | None = None,
    ) -> "OperationResult":
        return cls(ResultStatus.SUCCESS, changed, code, message, data or {})

    @classmethod
    def failure(
        cls,
        code: str,
        message: str,
        *,
        changed: bool = False,
        data: Mapping[str, object] | None = None,
    ) -> "OperationResult":
        return cls(ResultStatus.FAILURE, changed, code, message, data or {})

    @classmethod
    def unsupported(
        cls,
        code: str,
        message: str,
        *,
        data: Mapping[str, object] | None = None,
    ) -> "OperationResult":
        return cls(ResultStatus.UNSUPPORTED, False, code, message, data or {})

    @classmethod
    def not_implemented(
        cls,
        code: str,
        message: str,
        *,
        data: Mapping[str, object] | None = None,
    ) -> "OperationResult":
        return cls(ResultStatus.NOT_IMPLEMENTED, False, code, message, data or {})

    @classmethod
    def error(
        cls,
        code: str,
        message: str,
        *,
        changed: bool = False,
        data: Mapping[str, object] | None = None,
    ) -> "OperationResult":
        return cls(ResultStatus.ERROR, changed, code, message, data or {})
