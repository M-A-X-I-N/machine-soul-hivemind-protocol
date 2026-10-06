"""Side-effect-free models for runtime-bound package environments."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence, runtime_checkable
from urllib.parse import parse_qsl, urlsplit, urlunsplit

from .context import OperationContext
from .result import OperationResult
from .runtime import RuntimeInstance


_SECRET_KEY = re.compile(
    r"(?:^|[_-])(password|passwd|token|secret|credential|credentials|auth|api[_-]?key)(?:$|[_-])",
    re.IGNORECASE,
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|secret|credential|auth|api[_-]?key)\s*=\s*[^&\s]+"
)
_URL_USERINFO = re.compile(
    r"(?i)([a-z][a-z0-9+.-]*://)[^/@\s:]+(?::[^/@\s]*)?@"
)


def _redact_string(value: str) -> str:
    """Redact obvious credential material while preserving useful diagnostics."""

    result = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=<redacted>", value)
    result = _URL_USERINFO.sub(r"\1<redacted>@", result)
    try:
        parsed = urlsplit(result)
    except ValueError:
        return result

    if parsed.scheme and parsed.netloc:
        hostname = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port is not None else ""
        if parsed.username is not None or parsed.password is not None:
            netloc = f"<redacted>@{hostname}{port}"
        else:
            netloc = parsed.netloc

        query_parts = []
        for key, item in parse_qsl(parsed.query, keep_blank_values=True):
            query_parts.append((key, "<redacted>" if _SECRET_KEY.search(key) else item))
        if query_parts != parse_qsl(parsed.query, keep_blank_values=True):
            from urllib.parse import urlencode
            query = urlencode(query_parts)
        else:
            query = parsed.query
        result = urlunsplit((parsed.scheme, netloc, parsed.path, query, parsed.fragment))
    return result


def redact_package_diagnostic(value: object) -> object:
    """Return a JSON-safe structure with obvious credential material redacted."""

    if isinstance(value, Mapping):
        return {
            str(key): (
                "<redacted>"
                if _SECRET_KEY.search(str(key))
                else redact_package_diagnostic(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_package_diagnostic(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _redact_string(str(value))


def _assert_secret_safe(value: object, *, field_name: str) -> None:
    redacted = redact_package_diagnostic(value)
    if redacted != value:
        raise ValueError(f"{field_name} contains credential-like material and cannot be persisted.")


def sanitize_package_operation_result(result: OperationResult) -> OperationResult:
    """Redact backend diagnostics before shared orchestration exposes them."""

    message = _redact_string(result.message)
    data = redact_package_diagnostic(dict(result.data))
    assert isinstance(data, dict)
    return OperationResult(
        result.status,
        result.changed,
        result.code,
        message,
        data,
    )


class PackageEnvironmentOwnershipKind(str, Enum):
    """Ownership/adoption state for one exact package environment."""

    UNMANAGED = "unmanaged"
    MACHINE_SOUL_CREATED = "machine_soul_created"
    ADOPTED = "adopted"
    EXTERNALLY_MANAGED_READ_ONLY = "externally_managed_read_only"
    PROJECT_OWNED = "project_owned"
    EPHEMERAL_UNMANAGED = "ephemeral_unmanaged"


class PackageMutationPolicy(str, Enum):
    """How aggressively Machine-Soul may reconcile an owned environment."""

    READ_ONLY = "read_only"
    MANAGED_ROOTS = "managed_roots"
    EXCLUSIVE = "exclusive"


class PackageObservationKind(str, Enum):
    """Whether an observed installed package is top-level or transitive."""

    TOP_LEVEL = "top_level"
    TRANSITIVE = "transitive"


class PackageRootStatus(str, Enum):
    """Backend verification status for one desired root."""

    SATISFIED = "satisfied"
    MISSING = "missing"
    UPDATE_REQUIRED = "update_required"


@dataclass(frozen=True)
class RuntimeInstanceRef:
    """Foreign-key-like exact reference to one runtime instance."""

    subject: str
    backend: str
    backend_key: str
    version: str
    architecture: str | None = None
    flavor: str | None = None
    distribution: str | None = None
    scope_subject: str | None = None

    def __post_init__(self) -> None:
        for name in ("subject", "backend", "backend_key", "version"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")
        if self.scope_subject is not None and not self.scope_subject.strip():
            raise ValueError("scope_subject cannot be empty.")

    @classmethod
    def from_instance(
        cls,
        instance: RuntimeInstance,
        *,
        scope_subject: str | None = None,
    ) -> "RuntimeInstanceRef":
        return cls(
            subject=instance.subject,
            backend=instance.backend,
            backend_key=instance.backend_key,
            version=instance.version,
            architecture=instance.architecture,
            flavor=instance.flavor,
            distribution=instance.distribution,
            scope_subject=scope_subject,
        )

    def matches_instance(
        self,
        instance: RuntimeInstance,
        *,
        scope_subject: str | None = None,
    ) -> bool:
        return (
            self.subject == instance.subject
            and self.backend == instance.backend
            and self.backend_key == instance.backend_key
            and self.version == instance.version
            and self.architecture == instance.architecture
            and self.flavor == instance.flavor
            and self.distribution == instance.distribution
            and self.scope_subject == scope_subject
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "backend": self.backend,
            "backend_key": self.backend_key,
            "version": self.version,
            "architecture": self.architecture,
            "flavor": self.flavor,
            "distribution": self.distribution,
            "scope_subject": self.scope_subject,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "RuntimeInstanceRef":
        return cls(
            subject=str(payload["subject"]),
            backend=str(payload["backend"]),
            backend_key=str(payload["backend_key"]),
            version=str(payload["version"]),
            architecture=str(payload["architecture"]) if payload.get("architecture") else None,
            flavor=str(payload["flavor"]) if payload.get("flavor") else None,
            distribution=str(payload["distribution"]) if payload.get("distribution") else None,
            scope_subject=str(payload["scope_subject"]) if payload.get("scope_subject") else None,
        )


@dataclass(frozen=True)
class PackageEnvironmentLocator:
    """Backend-specific environment locator without universal scope semantics."""

    kind: str
    values: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("Package environment locator kind cannot be empty.")
        copied = {str(key): str(value) for key, value in self.values.items()}
        if not copied or any(not key.strip() or not value.strip() for key, value in copied.items()):
            raise ValueError("Package environment locator values must be non-empty.")
        _assert_secret_safe(copied, field_name="Package environment locator")
        object.__setattr__(self, "values", MappingProxyType(copied))

    def __hash__(self) -> int:
        return hash((self.kind, tuple(sorted(self.values.items()))))

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind, "values": dict(self.values)}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "PackageEnvironmentLocator":
        values = payload.get("values")
        if not isinstance(values, Mapping):
            raise ValueError("Package environment locator values must be a mapping.")
        return cls(str(payload["kind"]), {str(key): str(value) for key, value in values.items()})


@dataclass(frozen=True)
class PackageEnvironmentIdentity:
    """Exact identity for one package-manager environment."""

    manager: str
    backend: str
    backend_key: str
    locator: PackageEnvironmentLocator
    classification: str
    runtime: RuntimeInstanceRef | None = None

    def __post_init__(self) -> None:
        for name in ("manager", "backend", "backend_key", "classification"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")

    def to_dict(self) -> dict[str, object]:
        return {
            "manager": self.manager,
            "backend": self.backend,
            "backend_key": self.backend_key,
            "locator": self.locator.to_dict(),
            "classification": self.classification,
            "runtime": self.runtime.to_dict() if self.runtime is not None else None,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "PackageEnvironmentIdentity":
        locator = payload.get("locator")
        if not isinstance(locator, Mapping):
            raise ValueError("Package environment identity locator must be a mapping.")
        runtime = payload.get("runtime")
        if runtime is not None and not isinstance(runtime, Mapping):
            raise ValueError("Package environment runtime reference must be a mapping.")
        return cls(
            manager=str(payload["manager"]),
            backend=str(payload["backend"]),
            backend_key=str(payload["backend_key"]),
            locator=PackageEnvironmentLocator.from_dict(locator),
            classification=str(payload["classification"]),
            runtime=RuntimeInstanceRef.from_dict(runtime) if runtime is not None else None,
        )


@dataclass(frozen=True)
class PackageEnvironment:
    """One exact observed package environment."""

    identity: PackageEnvironmentIdentity
    ownership: PackageEnvironmentOwnershipKind = PackageEnvironmentOwnershipKind.UNMANAGED
    mutation_policy: PackageMutationPolicy = PackageMutationPolicy.READ_ONLY
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.ownership, PackageEnvironmentOwnershipKind):
            raise TypeError("ownership must be PackageEnvironmentOwnershipKind.")
        if not isinstance(self.mutation_policy, PackageMutationPolicy):
            raise TypeError("mutation_policy must be PackageMutationPolicy.")
        mutable_owners = {
            PackageEnvironmentOwnershipKind.MACHINE_SOUL_CREATED,
            PackageEnvironmentOwnershipKind.ADOPTED,
        }
        if self.ownership not in mutable_owners and self.mutation_policy is not PackageMutationPolicy.READ_ONLY:
            raise ValueError("Unowned/external/project/ephemeral environments must be read-only.")
        copied = dict(self.metadata)
        _assert_secret_safe(copied, field_name="Package environment metadata")
        object.__setattr__(self, "metadata", MappingProxyType(copied))

    def to_dict(self) -> dict[str, object]:
        return {
            "identity": self.identity.to_dict(),
            "ownership": self.ownership.value,
            "mutation_policy": self.mutation_policy.value,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DesiredPackageRoot:
    """One manager-native desired package root."""

    backend_key: str
    native_specifier: str
    normalized_name: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.backend_key.strip() or not self.native_specifier.strip():
            raise ValueError("Desired package root key/specifier cannot be empty.")
        if self.normalized_name is not None and not self.normalized_name.strip():
            raise ValueError("normalized_name cannot be empty.")
        _assert_secret_safe(self.native_specifier, field_name="Desired package specifier")
        copied = dict(self.metadata)
        _assert_secret_safe(copied, field_name="Desired package metadata")
        object.__setattr__(self, "metadata", MappingProxyType(copied))

    def to_dict(self) -> dict[str, object]:
        return {
            "backend_key": self.backend_key,
            "native_specifier": self.native_specifier,
            "normalized_name": self.normalized_name,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ObservedPackage:
    """One installed package observation within one exact environment."""

    backend_key: str
    native_name: str
    version: str | None
    kind: PackageObservationKind
    normalized_name: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.backend_key.strip() or not self.native_name.strip():
            raise ValueError("Observed package key/name cannot be empty.")
        if self.version is not None and not self.version.strip():
            raise ValueError("Observed package version cannot be empty.")
        if not isinstance(self.kind, PackageObservationKind):
            raise TypeError("kind must be PackageObservationKind.")
        copied = dict(self.metadata)
        _assert_secret_safe(copied, field_name="Observed package metadata")
        object.__setattr__(self, "metadata", MappingProxyType(copied))

    def to_dict(self) -> dict[str, object]:
        return {
            "backend_key": self.backend_key,
            "native_name": self.native_name,
            "version": self.version,
            "kind": self.kind.value,
            "normalized_name": self.normalized_name,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class PackageInventory:
    """Observed package set for one exact environment."""

    environment_key: str
    packages: tuple[ObservedPackage, ...]

    def __post_init__(self) -> None:
        if not self.environment_key.strip():
            raise ValueError("environment_key cannot be empty.")
        keys = [package.backend_key for package in self.packages]
        if len(keys) != len(set(keys)):
            raise ValueError("Package inventory contains duplicate backend keys.")

    def to_dict(self) -> dict[str, object]:
        return {
            "environment_key": self.environment_key,
            "packages": [package.to_dict() for package in self.packages],
        }


@dataclass(frozen=True)
class PackageRootResolution:
    """Backend verification mapping from desired root to observed identity."""

    desired_key: str
    status: PackageRootStatus
    observed_key: str | None = None
    removal_key: str | None = None

    def __post_init__(self) -> None:
        if not self.desired_key.strip():
            raise ValueError("desired_key cannot be empty.")
        if not isinstance(self.status, PackageRootStatus):
            raise TypeError("status must be PackageRootStatus.")
        if self.status in {PackageRootStatus.SATISFIED, PackageRootStatus.UPDATE_REQUIRED}:
            if self.removal_key is None or not self.removal_key.strip():
                raise ValueError("Satisfied/update-required roots need an exact removal key.")
        if self.status is PackageRootStatus.SATISFIED:
            if self.observed_key is None or not self.observed_key.strip():
                raise ValueError("Satisfied roots need an exact observed key.")

    def to_dict(self) -> dict[str, object]:
        return {
            "desired_key": self.desired_key,
            "status": self.status.value,
            "observed_key": self.observed_key,
            "removal_key": self.removal_key,
        }


@dataclass(frozen=True)
class PackageVerification:
    """Backend verification result for all desired roots."""

    environment_key: str
    roots: tuple[PackageRootResolution, ...]

    def __post_init__(self) -> None:
        if not self.environment_key.strip():
            raise ValueError("environment_key cannot be empty.")
        keys = [root.desired_key for root in self.roots]
        if len(keys) != len(set(keys)):
            raise ValueError("Package verification contains duplicate desired root keys.")

    @property
    def by_key(self) -> Mapping[str, PackageRootResolution]:
        return MappingProxyType({root.desired_key: root for root in self.roots})

    def to_dict(self) -> dict[str, object]:
        return {
            "environment_key": self.environment_key,
            "roots": [root.to_dict() for root in self.roots],
        }


@dataclass(frozen=True)
class PackageRemovalTarget:
    """Exact backend removal identity for an owned or observed top-level package."""

    removal_key: str
    native_name: str | None = None
    normalized_name: str | None = None

    def __post_init__(self) -> None:
        if not self.removal_key.strip():
            raise ValueError("removal_key cannot be empty.")


@dataclass(frozen=True)
class PackageRootOwnership:
    """Persisted ownership of one desired package root."""

    backend_key: str
    native_specifier: str
    normalized_name: str | None
    observed_key: str
    removal_key: str

    def __post_init__(self) -> None:
        for name in ("backend_key", "native_specifier", "observed_key", "removal_key"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} cannot be empty.")
        _assert_secret_safe(self.native_specifier, field_name="Owned package specifier")

    @classmethod
    def from_desired(
        cls,
        desired: DesiredPackageRoot,
        resolution: PackageRootResolution,
    ) -> "PackageRootOwnership":
        if resolution.status is not PackageRootStatus.SATISFIED:
            raise ValueError("Only satisfied desired roots can become owned.")
        assert resolution.observed_key is not None
        assert resolution.removal_key is not None
        return cls(
            backend_key=desired.backend_key,
            native_specifier=desired.native_specifier,
            normalized_name=desired.normalized_name,
            observed_key=resolution.observed_key,
            removal_key=resolution.removal_key,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "backend_key": self.backend_key,
            "native_specifier": self.native_specifier,
            "normalized_name": self.normalized_name,
            "observed_key": self.observed_key,
            "removal_key": self.removal_key,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "PackageRootOwnership":
        return cls(
            backend_key=str(payload["backend_key"]),
            native_specifier=str(payload["native_specifier"]),
            normalized_name=str(payload["normalized_name"]) if payload.get("normalized_name") else None,
            observed_key=str(payload["observed_key"]),
            removal_key=str(payload["removal_key"]),
        )


@dataclass(frozen=True)
class PackageEnvironmentOwnership:
    """Persisted Machine-Soul ownership for one exact package environment."""

    host: str
    identity: PackageEnvironmentIdentity
    ownership: PackageEnvironmentOwnershipKind
    mutation_policy: PackageMutationPolicy
    roots: tuple[PackageRootOwnership, ...] = ()
    scope_subject: str | None = None
    schema: int = 1

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("host cannot be empty.")
        if self.ownership not in {
            PackageEnvironmentOwnershipKind.MACHINE_SOUL_CREATED,
            PackageEnvironmentOwnershipKind.ADOPTED,
        }:
            raise ValueError("Persisted package environment ownership must be created or adopted.")
        if self.scope_subject is not None and not self.scope_subject.strip():
            raise ValueError("scope_subject cannot be empty.")
        keys = [root.backend_key for root in self.roots]
        if len(keys) != len(set(keys)):
            raise ValueError("Package environment ownership contains duplicate root keys.")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "host": self.host,
            "identity": self.identity.to_dict(),
            "ownership": self.ownership.value,
            "mutation_policy": self.mutation_policy.value,
            "roots": [root.to_dict() for root in self.roots],
            "scope_subject": self.scope_subject,
        }


@dataclass(frozen=True)
class PackageEnvironmentDesiredState:
    """Desired root inventory for one exact already-owned environment."""

    environment: PackageEnvironmentIdentity
    roots: tuple[DesiredPackageRoot, ...]

    def __post_init__(self) -> None:
        keys = [root.backend_key for root in self.roots]
        if len(keys) != len(set(keys)):
            raise ValueError("Desired package roots contain duplicate backend keys.")

    @property
    def desired_keys(self) -> frozenset[str]:
        return frozenset(root.backend_key for root in self.roots)

    def to_dict(self) -> dict[str, object]:
        return {
            "environment": self.environment.to_dict(),
            "roots": [root.to_dict() for root in self.roots],
        }


@runtime_checkable
class PackageEnvironmentBackend(Protocol):
    """Concrete package-environment contract consumed by shared reconciliation."""

    manager: str
    name: str

    def ownership_scope(self, context: OperationContext) -> str | None:
        """Return backend-defined ownership scope; None means host-wide."""
        ...

    def discover_environments(self, context: OperationContext) -> tuple[PackageEnvironment, ...]:
        """Discover exact package environments without mutating them."""
        ...

    def check_tool(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> OperationResult:
        """Verify the package-manager tool is available for this environment."""
        ...

    def discover_inventory(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
    ) -> PackageInventory:
        """Discover packages inside the exact identified environment."""
        ...

    def verify(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        desired_roots: Sequence[DesiredPackageRoot],
        inventory: PackageInventory,
        owned_roots: Sequence[PackageRootOwnership],
    ) -> PackageVerification:
        """Map desired roots to exact observed package/removal identities.

        Existing Machine-Soul root provenance is supplied so a backend can
        distinguish a previously verified native specifier from an unrelated
        package that merely has the same normalized identity.
        """
        ...

    def install(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        """Install one desired root through manager-native semantics."""
        ...

    def update(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        root: DesiredPackageRoot,
    ) -> OperationResult:
        """Update/reconcile one already-present desired root."""
        ...

    def remove(
        self,
        context: OperationContext,
        environment: PackageEnvironment,
        target: PackageRemovalTarget,
    ) -> OperationResult:
        """Remove one exact owned or explicitly-exclusive top-level package."""
        ...
