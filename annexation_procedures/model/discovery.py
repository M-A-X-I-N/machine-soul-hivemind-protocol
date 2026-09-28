"""Typed discovery observations and semantic assessments."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import math
from types import MappingProxyType
from typing import Mapping


JsonPrimitive = str | int | float | bool | None
JsonValue = JsonPrimitive | Mapping[str, "JsonValue"] | tuple["JsonValue", ...]


def _freeze_json(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Discovery data cannot contain NaN or infinity.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, JsonValue] = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise TypeError("Discovery data keys must be strings.")
            frozen[key] = _freeze_json(value[key])
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    raise TypeError(f"Discovery data is not JSON-compatible: {type(value).__name__}.")


def _thaw_json(value: JsonValue) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _validate_nonempty(value: str, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")


class ObservationAuthority(str, Enum):
    """How directly a raw observation establishes the fact it records."""

    DIRECT = "direct"
    CORRELATED = "correlated"
    INFERRED = "inferred"
    HINT = "hint"


class EvidenceStrength(str, Enum):
    """Strength of effective-configuration evidence."""

    RUNTIME = "runtime"
    APPLICATION = "application"
    RESOLUTION = "resolution"
    CONVENTION = "convention"
    NONE = "none"

    @property
    def rank(self) -> int:
        return {
            EvidenceStrength.NONE: 0,
            EvidenceStrength.CONVENTION: 1,
            EvidenceStrength.RESOLUTION: 2,
            EvidenceStrength.APPLICATION: 3,
            EvidenceStrength.RUNTIME: 4,
        }[self]


class TriState(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class InstallationPresence(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


class InstallationScope(str, Enum):
    USER = "user"
    MACHINE = "machine"
    PACKAGE_USER = "package_user"
    UNKNOWN = "unknown"


class InstallationOwnership(str, Enum):
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    STALE = "stale"
    UNKNOWN = "unknown"


class VerificationConclusion(str, Enum):
    EFFECTIVE = "effective"
    NOT_EFFECTIVE = "not_effective"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class DiscoveryObservation:
    kind: str
    source: str
    authority: ObservationAuthority
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_nonempty(self.kind, "kind")
        _validate_nonempty(self.source, "source")
        if not isinstance(self.authority, ObservationAuthority):
            raise TypeError("authority must be an ObservationAuthority.")
        frozen = _freeze_json(dict(self.data))
        assert isinstance(frozen, Mapping)
        object.__setattr__(self, "data", frozen)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "source": self.source,
            "authority": self.authority.value,
            "data": _thaw_json(self.data),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "DiscoveryObservation":
        return cls(
            kind=str(payload["kind"]),
            source=str(payload["source"]),
            authority=ObservationAuthority(str(payload["authority"])),
            data=_mapping(payload.get("data", {}), "observation data"),
        )


@dataclass(frozen=True)
class InstallationCandidate:
    native_identity: str
    display_identity: str | None = None
    version: str | None = None
    paths: tuple[str, ...] = ()
    scope: InstallationScope = InstallationScope.UNKNOWN
    registration_kind: str | None = None
    acquisition_channel: str | None = None
    acquisition_authority: ObservationAuthority | None = None
    preferred_match: TriState = TriState.UNKNOWN
    manageable_by_preferred_strategy: TriState = TriState.UNKNOWN
    ownership: InstallationOwnership = InstallationOwnership.UNKNOWN
    uninstall_identity: str | None = None
    observations: tuple[DiscoveryObservation, ...] = ()

    def __post_init__(self) -> None:
        _validate_nonempty(self.native_identity, "native_identity")
        for name in ("display_identity", "version", "registration_kind", "acquisition_channel", "uninstall_identity"):
            value = getattr(self, name)
            if value is not None:
                _validate_nonempty(value, name)
        for path in self.paths:
            _validate_nonempty(path, "path")
        if len(set(self.paths)) != len(self.paths):
            raise ValueError("paths cannot contain duplicates.")
        if not isinstance(self.scope, InstallationScope):
            raise TypeError("scope must be an InstallationScope.")
        if self.acquisition_authority is not None and not isinstance(
            self.acquisition_authority, ObservationAuthority
        ):
            raise TypeError("acquisition_authority must be an ObservationAuthority or None.")
        if self.acquisition_channel is None and self.acquisition_authority is not None:
            raise ValueError("acquisition_authority requires acquisition_channel.")
        if not isinstance(self.preferred_match, TriState):
            raise TypeError("preferred_match must be a TriState.")
        if not isinstance(self.manageable_by_preferred_strategy, TriState):
            raise TypeError("manageable_by_preferred_strategy must be a TriState.")
        if not isinstance(self.ownership, InstallationOwnership):
            raise TypeError("ownership must be an InstallationOwnership.")
        if not all(isinstance(item, DiscoveryObservation) for item in self.observations):
            raise TypeError("observations must contain DiscoveryObservation values.")

    def to_dict(self) -> dict[str, object]:
        return {
            "native_identity": self.native_identity,
            "display_identity": self.display_identity,
            "version": self.version,
            "paths": list(self.paths),
            "scope": self.scope.value,
            "registration_kind": self.registration_kind,
            "acquisition_channel": self.acquisition_channel,
            "acquisition_authority": (
                self.acquisition_authority.value if self.acquisition_authority else None
            ),
            "preferred_match": self.preferred_match.value,
            "manageable_by_preferred_strategy": self.manageable_by_preferred_strategy.value,
            "ownership": self.ownership.value,
            "uninstall_identity": self.uninstall_identity,
            "observations": [item.to_dict() for item in self.observations],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "InstallationCandidate":
        observations = _sequence(payload.get("observations", []), "candidate observations")
        return cls(
            native_identity=str(payload["native_identity"]),
            display_identity=_optional_string(payload.get("display_identity"), "display_identity"),
            version=_optional_string(payload.get("version"), "version"),
            paths=tuple(str(item) for item in _sequence(payload.get("paths", []), "paths")),
            scope=InstallationScope(str(payload.get("scope", InstallationScope.UNKNOWN.value))),
            registration_kind=_optional_string(payload.get("registration_kind"), "registration_kind"),
            acquisition_channel=_optional_string(payload.get("acquisition_channel"), "acquisition_channel"),
            acquisition_authority=(
                ObservationAuthority(str(payload["acquisition_authority"]))
                if payload.get("acquisition_authority") is not None
                else None
            ),
            preferred_match=TriState(str(payload.get("preferred_match", TriState.UNKNOWN.value))),
            manageable_by_preferred_strategy=TriState(
                str(payload.get("manageable_by_preferred_strategy", TriState.UNKNOWN.value))
            ),
            ownership=InstallationOwnership(
                str(payload.get("ownership", InstallationOwnership.UNKNOWN.value))
            ),
            uninstall_identity=_optional_string(payload.get("uninstall_identity"), "uninstall_identity"),
            observations=tuple(
                DiscoveryObservation.from_dict(_mapping(item, "candidate observation"))
                for item in observations
            ),
        )


@dataclass(frozen=True)
class InstallationAssessment:
    presence: InstallationPresence
    candidates: tuple[InstallationCandidate, ...] = ()
    preferred_candidate_index: int | None = None
    machine_soul_state: InstallationOwnership = InstallationOwnership.UNKNOWN
    observations: tuple[DiscoveryObservation, ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.presence, InstallationPresence):
            raise TypeError("presence must be an InstallationPresence.")
        if not all(isinstance(item, InstallationCandidate) for item in self.candidates):
            raise TypeError("candidates must contain InstallationCandidate values.")
        if not isinstance(self.machine_soul_state, InstallationOwnership):
            raise TypeError("machine_soul_state must be an InstallationOwnership.")
        if not all(isinstance(item, DiscoveryObservation) for item in self.observations):
            raise TypeError("observations must contain DiscoveryObservation values.")
        for error in self.errors:
            _validate_nonempty(error, "error")

        if self.presence is InstallationPresence.ABSENT and self.candidates:
            raise ValueError("ABSENT assessments cannot contain installation candidates.")
        if self.presence is InstallationPresence.PRESENT and not self.candidates:
            raise ValueError("PRESENT assessments require at least one candidate.")
        if self.presence is InstallationPresence.AMBIGUOUS and not self.candidates:
            raise ValueError("AMBIGUOUS assessments require candidate evidence.")

        if self.preferred_candidate_index is not None:
            if not isinstance(self.preferred_candidate_index, int):
                raise TypeError("preferred_candidate_index must be int or None.")
            if not 0 <= self.preferred_candidate_index < len(self.candidates):
                raise ValueError("preferred_candidate_index is outside candidates.")
            if (
                self.candidates[self.preferred_candidate_index].preferred_match
                is not TriState.YES
            ):
                raise ValueError("preferred candidate must explicitly match the preferred strategy.")

    @property
    def preferred_candidate(self) -> InstallationCandidate | None:
        if self.preferred_candidate_index is None:
            return None
        return self.candidates[self.preferred_candidate_index]

    def to_dict(self) -> dict[str, object]:
        return {
            "presence": self.presence.value,
            "candidates": [item.to_dict() for item in self.candidates],
            "preferred_candidate_index": self.preferred_candidate_index,
            "machine_soul_state": self.machine_soul_state.value,
            "observations": [item.to_dict() for item in self.observations],
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "InstallationAssessment":
        candidates = _sequence(payload.get("candidates", []), "assessment candidates")
        observations = _sequence(payload.get("observations", []), "assessment observations")
        preferred_index = payload.get("preferred_candidate_index")
        if preferred_index is not None and not isinstance(preferred_index, int):
            raise TypeError("preferred_candidate_index must be int or None.")
        return cls(
            presence=InstallationPresence(str(payload["presence"])),
            candidates=tuple(
                InstallationCandidate.from_dict(_mapping(item, "installation candidate"))
                for item in candidates
            ),
            preferred_candidate_index=preferred_index,
            machine_soul_state=InstallationOwnership(
                str(payload.get("machine_soul_state", InstallationOwnership.UNKNOWN.value))
            ),
            observations=tuple(
                DiscoveryObservation.from_dict(_mapping(item, "assessment observation"))
                for item in observations
            ),
            errors=tuple(str(item) for item in _sequence(payload.get("errors", []), "errors")),
        )


@dataclass(frozen=True)
class VerificationObservation:
    kind: str
    source: str
    evidence: EvidenceStrength
    supports: VerificationConclusion
    data: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_nonempty(self.kind, "kind")
        _validate_nonempty(self.source, "source")
        if not isinstance(self.evidence, EvidenceStrength):
            raise TypeError("evidence must be an EvidenceStrength.")
        if self.evidence is EvidenceStrength.NONE:
            raise ValueError("A concrete verification observation cannot have NONE evidence.")
        if not isinstance(self.supports, VerificationConclusion):
            raise TypeError("supports must be a VerificationConclusion.")
        frozen = _freeze_json(dict(self.data))
        assert isinstance(frozen, Mapping)
        object.__setattr__(self, "data", frozen)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "source": self.source,
            "evidence": self.evidence.value,
            "supports": self.supports.value,
            "data": _thaw_json(self.data),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "VerificationObservation":
        return cls(
            kind=str(payload["kind"]),
            source=str(payload["source"]),
            evidence=EvidenceStrength(str(payload["evidence"])),
            supports=VerificationConclusion(str(payload["supports"])),
            data=_mapping(payload.get("data", {}), "verification observation data"),
        )


@dataclass(frozen=True)
class VerificationAssessment:
    conclusion: VerificationConclusion
    strongest_evidence: EvidenceStrength
    observations: tuple[VerificationObservation, ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.conclusion, VerificationConclusion):
            raise TypeError("conclusion must be a VerificationConclusion.")
        if not isinstance(self.strongest_evidence, EvidenceStrength):
            raise TypeError("strongest_evidence must be an EvidenceStrength.")
        if not all(isinstance(item, VerificationObservation) for item in self.observations):
            raise TypeError("observations must contain VerificationObservation values.")
        for error in self.errors:
            _validate_nonempty(error, "error")

        if (
            self.strongest_evidence is EvidenceStrength.NONE
            and self.conclusion is not VerificationConclusion.INDETERMINATE
        ):
            raise ValueError("Effective/not-effective conclusions require non-NONE evidence.")

        observed_max = max(
            (item.evidence.rank for item in self.observations),
            default=0,
        )
        if observed_max != self.strongest_evidence.rank:
            raise ValueError("strongest_evidence must equal the strongest observation evidence.")
        if self.conclusion is not VerificationConclusion.INDETERMINATE:
            strongest_support = {
                item.supports
                for item in self.observations
                if item.evidence.rank == observed_max
            }
            if self.conclusion not in strongest_support:
                raise ValueError("conclusion must be supported by a strongest-evidence observation.")

    def to_dict(self) -> dict[str, object]:
        return {
            "conclusion": self.conclusion.value,
            "strongest_evidence": self.strongest_evidence.value,
            "observations": [item.to_dict() for item in self.observations],
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "VerificationAssessment":
        observations = _sequence(payload.get("observations", []), "verification observations")
        return cls(
            conclusion=VerificationConclusion(str(payload["conclusion"])),
            strongest_evidence=EvidenceStrength(str(payload["strongest_evidence"])),
            observations=tuple(
                VerificationObservation.from_dict(_mapping(item, "verification observation"))
                for item in observations
            ),
            errors=tuple(str(item) for item in _sequence(payload.get("errors", []), "errors")),
        )


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")
    if not all(isinstance(key, str) for key in value):
        raise TypeError(f"{name} keys must be strings.")
    return value


def _sequence(value: object, name: str) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be a list or tuple.")
    return tuple(value)


def _optional_string(value: object, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string or None.")
    return value


def assert_json_serializable(value: object) -> None:
    """Internal test/helper guard for machine-output compatibility."""
    json.dumps(value, sort_keys=True, allow_nan=False)
