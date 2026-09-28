"""Shared package-environment ownership, inventory, and reconciliation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .model import (
    DesiredPackageRoot,
    OperationContext,
    OperationResult,
    PackageEnvironment,
    PackageEnvironmentBackend,
    PackageEnvironmentDesiredState,
    PackageEnvironmentIdentity,
    PackageEnvironmentOwnership,
    PackageEnvironmentOwnershipKind,
    PackageInventory,
    PackageMutationPolicy,
    PackageObservationKind,
    PackageRemovalTarget,
    PackageRootOwnership,
    PackageRootStatus,
    PackageVerification,
    ResultStatus,
    RuntimeInstance,
    RuntimeInstanceRef,
    sanitize_package_operation_result,
)
from .state import read_json_state, write_json_state


_PACKAGE_ENVIRONMENT_STATE_SCHEMA = 1


class PackageEnvironmentStateError(RuntimeError):
    """Persisted package-environment state is malformed or unsafe."""


def _safe_component(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def package_environment_ownership_path(
    context: OperationContext,
    identity: PackageEnvironmentIdentity,
    *,
    scope_subject: str | None = None,
) -> Path:
    """Canonical ownership path for one exact package environment."""

    root = (
        context.repository_root
        / "scratch"
        / "state"
        / "package_environment"
        / context.host
    )
    if scope_subject is not None:
        if not scope_subject.strip():
            raise ValueError("Package environment ownership scope cannot be empty.")
        root = root / "scoped" / _safe_component(scope_subject)
    identity_key = json.dumps(
        [identity.manager, identity.backend, identity.backend_key],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (
        root
        / _safe_component(identity.manager)
        / _safe_component(identity.backend)
        / f"{_safe_component(identity_key)}.json"
    )


def _ownership_from_payload(payload: dict[str, object]) -> PackageEnvironmentOwnership:
    if payload.get("schema") != _PACKAGE_ENVIRONMENT_STATE_SCHEMA:
        raise PackageEnvironmentStateError(
            f"Unsupported package environment ownership schema: {payload.get('schema')!r}."
        )
    identity_raw = payload.get("identity")
    roots_raw = payload.get("roots", [])
    if not isinstance(identity_raw, dict):
        raise PackageEnvironmentStateError("Package environment identity state is malformed.")
    if not isinstance(roots_raw, list) or not all(isinstance(item, dict) for item in roots_raw):
        raise PackageEnvironmentStateError("Package environment root ownership state is malformed.")
    try:
        return PackageEnvironmentOwnership(
            host=str(payload["host"]),
            identity=PackageEnvironmentIdentity.from_dict(identity_raw),
            ownership=PackageEnvironmentOwnershipKind(str(payload["ownership"])),
            mutation_policy=PackageMutationPolicy(str(payload["mutation_policy"])),
            roots=tuple(PackageRootOwnership.from_dict(item) for item in roots_raw),
            scope_subject=(
                str(payload["scope_subject"])
                if payload.get("scope_subject") not in (None, "")
                else None
            ),
            schema=_PACKAGE_ENVIRONMENT_STATE_SCHEMA,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise PackageEnvironmentStateError(
            f"Package environment ownership state is invalid: {exc}"
        ) from exc


def read_package_environment_ownerships(
    context: OperationContext,
) -> tuple[PackageEnvironmentOwnership, ...]:
    """Read all package-environment ownership records for the current host."""

    root = (
        context.repository_root
        / "scratch"
        / "state"
        / "package_environment"
        / context.host
    )
    if not root.is_dir():
        return ()

    states: list[PackageEnvironmentOwnership] = []
    for path in sorted(root.rglob("*.json")):
        payload = read_json_state(path)
        if payload is None:
            continue
        state = _ownership_from_payload(payload)
        if state.host != context.host:
            raise PackageEnvironmentStateError(
                "Package environment ownership path and host identity disagree."
            )
        expected = package_environment_ownership_path(
            context,
            state.identity,
            scope_subject=state.scope_subject,
        )
        if path != expected:
            raise PackageEnvironmentStateError(
                "Package environment ownership is stored under the wrong identity key."
            )
        states.append(state)
    return tuple(states)


def _write_package_environment_ownership(
    context: OperationContext,
    state: PackageEnvironmentOwnership,
) -> None:
    write_json_state(
        package_environment_ownership_path(
            context,
            state.identity,
            scope_subject=state.scope_subject,
        ),
        state.to_dict(),
    )


def _backend_scope(
    backend: PackageEnvironmentBackend,
    context: OperationContext,
) -> tuple[str | None, OperationResult | None]:
    resolver = getattr(backend, "ownership_scope", None)
    if resolver is None:
        return None, None
    try:
        scope_subject = resolver(context)
    except Exception as exc:
        return None, OperationResult.error(
            "package_environment_ownership_scope_failed",
            f"Package backend ownership-scope resolution failed: {exc}",
        )
    if scope_subject is not None and (
        not isinstance(scope_subject, str) or not scope_subject.strip()
    ):
        return None, OperationResult.error(
            "package_environment_ownership_scope_invalid",
            "Package backend ownership scope must be a non-empty string or None.",
        )
    return scope_subject, None


def _validate_backend(
    backend: PackageEnvironmentBackend,
    desired: PackageEnvironmentDesiredState | None = None,
) -> OperationResult | None:
    if not backend.manager.strip() or not backend.name.strip():
        return OperationResult.error(
            "package_environment_backend_identity_invalid",
            "Package backend manager/name cannot be empty.",
        )
    if desired is not None:
        identity = desired.environment
        if identity.manager != backend.manager or identity.backend != backend.name:
            return OperationResult.failure(
                "package_environment_backend_mismatch",
                "Desired package environment belongs to a different manager/backend.",
                data={
                    "desired_manager": identity.manager,
                    "desired_backend": identity.backend,
                    "backend_manager": backend.manager,
                    "backend": backend.name,
                },
            )
    return None


def _discover_environments(
    backend: PackageEnvironmentBackend,
    context: OperationContext,
) -> tuple[tuple[PackageEnvironment, ...], OperationResult | None]:
    try:
        environments = tuple(backend.discover_environments(context))
    except Exception as exc:
        return (), OperationResult.error(
            "package_environment_discovery_failed",
            f"Package environment discovery failed: {exc}",
        )

    keys: set[str] = set()
    for environment in environments:
        identity = environment.identity
        if identity.manager == backend.manager and identity.backend == backend.name:
            if identity.backend_key in keys:
                return (), OperationResult.failure(
                    "package_environment_discovery_ambiguous",
                    "Package backend returned duplicate exact environment keys.",
                    data={"backend_key": identity.backend_key},
                )
            keys.add(identity.backend_key)
    return environments, None


def _exact_environment(
    environments: Iterable[PackageEnvironment],
    identity: PackageEnvironmentIdentity,
) -> PackageEnvironment | None:
    matches = [
        environment
        for environment in environments
        if environment.identity.manager == identity.manager
        and environment.identity.backend == identity.backend
        and environment.identity.backend_key == identity.backend_key
    ]
    if len(matches) != 1:
        return None
    return matches[0]


def _ownership_for_identity(
    context: OperationContext,
    identity: PackageEnvironmentIdentity,
    scope_subject: str | None,
) -> tuple[PackageEnvironmentOwnership | None, OperationResult | None]:
    try:
        states = read_package_environment_ownerships(context)
    except (PackageEnvironmentStateError, ValueError) as exc:
        return None, OperationResult.error(
            "package_environment_provenance_invalid",
            str(exc),
        )

    scoped = [
        state
        for state in states
        if state.scope_subject == scope_subject
        and state.identity.manager == identity.manager
        and state.identity.backend_key == identity.backend_key
    ]
    foreign = [state for state in scoped if state.identity.backend != identity.backend]
    if foreign:
        return None, OperationResult.failure(
            "package_environment_backend_migration_required",
            "Machine-Soul already owns this exact environment key through another backend.",
            data={"owned_backends": sorted({state.identity.backend for state in foreign})},
        )
    exact = [state for state in scoped if state.identity.backend == identity.backend]
    if len(exact) > 1:
        return None, OperationResult.error(
            "package_environment_provenance_ambiguous",
            "Multiple package environment ownership records match one exact identity.",
        )
    return (exact[0] if exact else None), None


def _adoptable(environment: PackageEnvironment) -> bool:
    return environment.ownership is PackageEnvironmentOwnershipKind.UNMANAGED


def _own_environment(
    context: OperationContext,
    backend: PackageEnvironmentBackend,
    backend_key: str,
    *,
    ownership: PackageEnvironmentOwnershipKind,
    mutation_policy: PackageMutationPolicy,
) -> OperationResult:
    invalid = _validate_backend(backend)
    if invalid is not None:
        return invalid
    if ownership not in {
        PackageEnvironmentOwnershipKind.ADOPTED,
        PackageEnvironmentOwnershipKind.MACHINE_SOUL_CREATED,
    }:
        raise ValueError("Package environment can only be adopted or registered as created.")

    scope_subject, error = _backend_scope(backend, context)
    if error is not None:
        return error
    environments, error = _discover_environments(backend, context)
    if error is not None:
        return error

    matches = [
        item
        for item in environments
        if item.identity.manager == backend.manager
        and item.identity.backend == backend.name
        and item.identity.backend_key == backend_key
    ]
    if len(matches) != 1:
        return OperationResult.failure(
            "package_environment_not_unique",
            "Environment ownership requires exactly one matching backend environment.",
            data={"backend_key": backend_key, "match_count": len(matches)},
        )
    environment = matches[0]
    existing, error = _ownership_for_identity(
        context,
        environment.identity,
        scope_subject,
    )
    if error is not None:
        return error
    if existing is not None:
        if existing.identity != environment.identity:
            return OperationResult.failure(
                "package_environment_provenance_mismatch",
                "Owned package environment identity no longer matches exact discovery.",
                data={
                    "owned": existing.identity.to_dict(),
                    "observed": environment.identity.to_dict(),
                },
            )
        return OperationResult.success(
            "package_environment_owned",
            "Package environment is already owned by Machine-Soul.",
            data={"environment": environment.to_dict()},
        )

    if not _adoptable(environment):
        return OperationResult.failure(
            "package_environment_not_adoptable",
            "External, project-owned, and ephemeral environments are not implicitly adoptable.",
            data={"environment": environment.to_dict()},
        )

    state = PackageEnvironmentOwnership(
        host=context.host,
        identity=environment.identity,
        ownership=ownership,
        mutation_policy=mutation_policy,
        scope_subject=scope_subject,
    )
    if context.dry_run:
        return OperationResult.success(
            "would_own_package_environment",
            "Package environment ownership would be recorded.",
            data={"ownership": state.to_dict()},
        )

    _write_package_environment_ownership(context, state)
    return OperationResult.success(
        "package_environment_owned",
        "Package environment ownership was recorded.",
        changed=True,
        data={"ownership": state.to_dict()},
    )


def adopt_package_environment(
    context: OperationContext,
    backend: PackageEnvironmentBackend,
    backend_key: str,
    *,
    mutation_policy: PackageMutationPolicy = PackageMutationPolicy.MANAGED_ROOTS,
) -> OperationResult:
    """Explicitly adopt one exact pre-existing package environment."""

    return _own_environment(
        context,
        backend,
        backend_key,
        ownership=PackageEnvironmentOwnershipKind.ADOPTED,
        mutation_policy=mutation_policy,
    )


def register_created_package_environment(
    context: OperationContext,
    backend: PackageEnvironmentBackend,
    backend_key: str,
    *,
    mutation_policy: PackageMutationPolicy = PackageMutationPolicy.MANAGED_ROOTS,
) -> OperationResult:
    """Record an exact environment whose lifecycle was created by Machine-Soul."""

    return _own_environment(
        context,
        backend,
        backend_key,
        ownership=PackageEnvironmentOwnershipKind.MACHINE_SOUL_CREATED,
        mutation_policy=mutation_policy,
    )


def _effective_environment(
    observed: PackageEnvironment,
    ownership: PackageEnvironmentOwnership,
) -> PackageEnvironment:
    return PackageEnvironment(
        identity=observed.identity,
        ownership=ownership.ownership,
        mutation_policy=ownership.mutation_policy,
        metadata=observed.metadata,
    )


def _safe_backend_result(result: OperationResult) -> OperationResult:
    try:
        return sanitize_package_operation_result(result)
    except Exception as exc:
        return OperationResult.error(
            "package_backend_diagnostic_invalid",
            f"Package backend returned an unsafe/non-serializable diagnostic: {exc}",
        )


def _tool_result(
    backend: PackageEnvironmentBackend,
    context: OperationContext,
    environment: PackageEnvironment,
) -> OperationResult:
    try:
        return _safe_backend_result(backend.check_tool(context, environment))
    except Exception as exc:
        return OperationResult.error(
            "package_tool_check_failed",
            f"Package-manager tool availability check failed: {exc}",
        )


def _inventory(
    backend: PackageEnvironmentBackend,
    context: OperationContext,
    environment: PackageEnvironment,
) -> tuple[PackageInventory | None, OperationResult | None]:
    try:
        inventory = backend.discover_inventory(context, environment)
    except Exception as exc:
        return None, OperationResult.error(
            "package_inventory_discovery_failed",
            f"Package inventory discovery failed: {exc}",
        )
    if inventory.environment_key != environment.identity.backend_key:
        return None, OperationResult.failure(
            "package_inventory_identity_mismatch",
            "Package inventory belongs to a different exact environment.",
        )
    return inventory, None


def _verification(
    backend: PackageEnvironmentBackend,
    context: OperationContext,
    environment: PackageEnvironment,
    desired_roots: tuple[DesiredPackageRoot, ...],
    inventory: PackageInventory,
) -> tuple[PackageVerification | None, OperationResult | None]:
    try:
        verification = backend.verify(context, environment, desired_roots, inventory)
    except Exception as exc:
        return None, OperationResult.error(
            "package_verification_failed",
            f"Package backend verification failed: {exc}",
        )
    if verification.environment_key != environment.identity.backend_key:
        return None, OperationResult.failure(
            "package_verification_identity_mismatch",
            "Package verification belongs to a different exact environment.",
        )
    expected = {root.backend_key for root in desired_roots}
    actual = set(verification.by_key)
    if actual != expected:
        return None, OperationResult.failure(
            "package_verification_incomplete",
            "Package backend verification did not resolve every desired root exactly once.",
            data={
                "missing": sorted(expected - actual),
                "extra": sorted(actual - expected),
            },
        )
    return verification, None


def _action_result(
    action: str,
    result: OperationResult,
    actions: list[dict[str, object]],
    *,
    changed: bool,
) -> tuple[bool, OperationResult | None]:
    safe = _safe_backend_result(result)
    actions.append({"action": action, "result": safe.to_dict()})
    changed = changed or safe.changed
    if safe.status is not ResultStatus.SUCCESS:
        return changed, OperationResult.error(
            "package_backend_mutation_failed",
            f"Package backend {action} operation failed.",
            changed=changed,
            data={"actions": actions, "backend_result": safe.to_dict()},
        )
    return changed, None


def reconcile_package_environment(
    context: OperationContext,
    backend: PackageEnvironmentBackend,
    desired: PackageEnvironmentDesiredState,
) -> OperationResult:
    """Reconcile desired roots in one exact explicitly-owned environment."""

    invalid = _validate_backend(backend, desired)
    if invalid is not None:
        return invalid
    scope_subject, error = _backend_scope(backend, context)
    if error is not None:
        return error
    environments, error = _discover_environments(backend, context)
    if error is not None:
        return error
    observed = _exact_environment(environments, desired.environment)
    if observed is None:
        return OperationResult.failure(
            "package_environment_missing",
            "Desired exact package environment was not discovered uniquely.",
            data={"environment": desired.environment.to_dict()},
        )
    if observed.identity != desired.environment:
        return OperationResult.failure(
            "package_environment_identity_mismatch",
            "Desired package environment identity differs from exact discovery.",
            data={
                "desired": desired.environment.to_dict(),
                "observed": observed.identity.to_dict(),
            },
        )

    ownership, error = _ownership_for_identity(context, desired.environment, scope_subject)
    if error is not None:
        return error
    if ownership is None:
        return OperationResult.failure(
            "package_environment_unmanaged",
            "Desired package environment is not owned; explicit adoption/creation ownership is required.",
            data={"environment": observed.to_dict()},
        )
    if ownership.identity != observed.identity:
        return OperationResult.failure(
            "package_environment_provenance_mismatch",
            "Owned package environment identity no longer matches exact discovery.",
        )
    if observed.ownership in {
        PackageEnvironmentOwnershipKind.EXTERNALLY_MANAGED_READ_ONLY,
        PackageEnvironmentOwnershipKind.PROJECT_OWNED,
        PackageEnvironmentOwnershipKind.EPHEMERAL_UNMANAGED,
    }:
        return OperationResult.failure(
            "package_environment_became_read_only",
            "Owned package environment is now classified as external/project/ephemeral and cannot be mutated.",
            data={"environment": observed.to_dict()},
        )

    environment = _effective_environment(observed, ownership)
    tool = _tool_result(backend, context, environment)
    if tool.status is not ResultStatus.SUCCESS:
        return OperationResult.failure(
            "package_tool_unavailable",
            "Package-manager tool is unavailable or unusable for this exact environment.",
            data={"backend_result": tool.to_dict()},
        )

    inventory, error = _inventory(backend, context, environment)
    if error is not None:
        return error
    assert inventory is not None
    verification, error = _verification(
        backend,
        context,
        environment,
        desired.roots,
        inventory,
    )
    if error is not None:
        return error
    assert verification is not None

    desired_by_key = {root.backend_key: root for root in desired.roots}
    owned_by_key = {root.backend_key: root for root in ownership.roots}
    install_keys = sorted(
        key
        for key, resolution in verification.by_key.items()
        if resolution.status is PackageRootStatus.MISSING
    )
    update_keys = sorted(
        key
        for key, resolution in verification.by_key.items()
        if resolution.status is PackageRootStatus.UPDATE_REQUIRED
    )
    remove_owned_keys = sorted(set(owned_by_key) - set(desired_by_key))

    referenced_observed = {
        resolution.observed_key
        for resolution in verification.roots
        if resolution.observed_key is not None
    }
    exclusive_unknown = [
        package
        for package in inventory.packages
        if ownership.mutation_policy is PackageMutationPolicy.EXCLUSIVE
        and package.kind is PackageObservationKind.TOP_LEVEL
        and package.backend_key not in referenced_observed
        and package.backend_key not in {
            item.observed_key for item in ownership.roots
        }
    ]

    planned = bool(install_keys or update_keys or remove_owned_keys or exclusive_unknown)
    if planned and ownership.mutation_policy is PackageMutationPolicy.READ_ONLY:
        return OperationResult.failure(
            "package_environment_read_only",
            "Package environment reconciliation requires mutation but its policy is read-only.",
            data={
                "install_keys": install_keys,
                "update_keys": update_keys,
                "remove_owned_keys": remove_owned_keys,
            },
        )

    if context.dry_run:
        return OperationResult.success(
            "would_reconcile_package_environment",
            "Package environment desired roots would be reconciled.",
            data={
                "desired": desired.to_dict(),
                "install_keys": install_keys,
                "update_keys": update_keys,
                "remove_owned_keys": remove_owned_keys,
                "exclusive_unknown_keys": [item.backend_key for item in exclusive_unknown],
                "preserved_unknown_top_level": [
                    item.backend_key
                    for item in inventory.packages
                    if item.kind is PackageObservationKind.TOP_LEVEL
                    and item.backend_key not in referenced_observed
                    and item.backend_key not in {
                        owned.observed_key for owned in ownership.roots
                    }
                    and item not in exclusive_unknown
                ],
            },
        )

    changed = False
    actions: list[dict[str, object]] = []

    for key in install_keys:
        result = backend.install(context, environment, desired_by_key[key])
        changed, failure = _action_result(
            f"install:{key}",
            result,
            actions,
            changed=changed,
        )
        if failure is not None:
            return failure

    for key in update_keys:
        result = backend.update(context, environment, desired_by_key[key])
        changed, failure = _action_result(
            f"update:{key}",
            result,
            actions,
            changed=changed,
        )
        if failure is not None:
            return failure

    for key in remove_owned_keys:
        owned = owned_by_key[key]
        result = backend.remove(
            context,
            environment,
            PackageRemovalTarget(
                owned.removal_key,
                normalized_name=owned.normalized_name,
            ),
        )
        changed, failure = _action_result(
            f"remove-owned:{key}",
            result,
            actions,
            changed=changed,
        )
        if failure is not None:
            return failure

    for package in exclusive_unknown:
        result = backend.remove(
            context,
            environment,
            PackageRemovalTarget(
                package.backend_key,
                native_name=package.native_name,
                normalized_name=package.normalized_name,
            ),
        )
        changed, failure = _action_result(
            f"remove-exclusive:{package.backend_key}",
            result,
            actions,
            changed=changed,
        )
        if failure is not None:
            return failure

    final_inventory, error = _inventory(backend, context, environment)
    if error is not None:
        return OperationResult.error(
            "package_reconciliation_verification_failed",
            error.message,
            changed=changed,
            data={"actions": actions},
        )
    assert final_inventory is not None
    final_verification, error = _verification(
        backend,
        context,
        environment,
        desired.roots,
        final_inventory,
    )
    if error is not None:
        return OperationResult.error(
            "package_reconciliation_verification_failed",
            error.message,
            changed=changed,
            data={"actions": actions},
        )
    assert final_verification is not None

    unsatisfied = [
        resolution.to_dict()
        for resolution in final_verification.roots
        if resolution.status is not PackageRootStatus.SATISFIED
    ]
    if unsatisfied:
        return OperationResult.error(
            "package_reconciliation_did_not_converge",
            "Package backend mutations did not satisfy every desired root.",
            changed=changed,
            data={"actions": actions, "unsatisfied": unsatisfied},
        )

    final_referenced = {
        resolution.observed_key
        for resolution in final_verification.roots
        if resolution.observed_key is not None
    }
    if ownership.mutation_policy is PackageMutationPolicy.EXCLUSIVE:
        leftover_unknown = [
            package.backend_key
            for package in final_inventory.packages
            if package.kind is PackageObservationKind.TOP_LEVEL
            and package.backend_key not in final_referenced
        ]
        if leftover_unknown:
            return OperationResult.error(
                "package_exclusive_reconciliation_did_not_converge",
                "Exclusive package environment still has unowned top-level packages.",
                changed=changed,
                data={"unknown_top_level": leftover_unknown, "actions": actions},
            )

    final_roots = tuple(
        PackageRootOwnership.from_desired(
            desired_by_key[key],
            final_verification.by_key[key],
        )
        for key in sorted(desired_by_key)
    )
    final_state = PackageEnvironmentOwnership(
        host=ownership.host,
        identity=ownership.identity,
        ownership=ownership.ownership,
        mutation_policy=ownership.mutation_policy,
        roots=final_roots,
        scope_subject=ownership.scope_subject,
    )
    state_changed = final_state != ownership
    if state_changed:
        _write_package_environment_ownership(context, final_state)

    return OperationResult.success(
        "package_environment_reconciled",
        "Package environment desired root inventory is reconciled.",
        changed=changed or state_changed,
        data={
            "actions": actions,
            "desired": desired.to_dict(),
            "inventory": final_inventory.to_dict(),
            "owned_roots": [root.to_dict() for root in final_roots],
        },
    )


def package_environment_runtime_removal_guard(
    context: OperationContext,
    runtime: RuntimeInstance,
    scope_subject: str | None = None,
) -> OperationResult:
    """Block runtime removal while an owned package environment is bound to it."""

    try:
        ownerships = read_package_environment_ownerships(context)
    except (PackageEnvironmentStateError, ValueError) as exc:
        return OperationResult.error(
            "package_environment_runtime_guard_state_invalid",
            str(exc),
        )

    blockers = [
        state
        for state in ownerships
        if state.identity.runtime is not None
        and state.identity.runtime.matches_instance(
            runtime,
            scope_subject=scope_subject,
        )
    ]
    if blockers:
        return OperationResult.failure(
            "runtime_has_owned_package_environments",
            "Runtime removal would orphan owned package environments.",
            data={
                "runtime": {
                    "subject": runtime.subject,
                    "backend": runtime.backend,
                    "backend_key": runtime.backend_key,
                    "version": runtime.version,
                },
                "package_environments": [
                    {
                        "manager": state.identity.manager,
                        "backend": state.identity.backend,
                        "backend_key": state.identity.backend_key,
                        "classification": state.identity.classification,
                        "owned_root_keys": [root.backend_key for root in state.roots],
                    }
                    for state in blockers
                ],
            },
        )

    return OperationResult.success(
        "runtime_package_environment_dependencies_clear",
        "No owned package environment depends on this runtime instance.",
    )
