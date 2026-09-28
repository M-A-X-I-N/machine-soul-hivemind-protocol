"""Shared runtime-instance ownership, adoption, and reconciliation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from .model import (
    OperationContext,
    OperationResult,
    ResultStatus,
    RuntimeBackend,
    RuntimeDesiredState,
    RuntimeInstance,
    RuntimeOwnership,
)
from .state import read_json_state, write_json_state


_RUNTIME_STATE_SCHEMA = 1


class RuntimeStateError(RuntimeError):
    """Persisted runtime ownership or backend observations are unsafe."""


def _safe_component(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def runtime_ownership_path(
    context: OperationContext,
    subject: str,
    backend: str,
    backend_key: str,
) -> Path:
    """Canonical machine/host-scoped ownership record for one runtime instance."""
    if not all(value.strip() for value in (subject, backend, backend_key)):
        raise ValueError("Runtime ownership identity fields cannot be empty.")
    return (
        context.repository_root
        / "scratch"
        / "state"
        / "runtime"
        / context.host
        / _safe_component(subject)
        / _safe_component(backend)
        / f"{_safe_component(backend_key)}.json"
    )


def _subject_state_root(context: OperationContext, subject: str) -> Path:
    return (
        context.repository_root
        / "scratch"
        / "state"
        / "runtime"
        / context.host
        / _safe_component(subject)
    )


def _ownership_from_payload(payload: dict[str, object]) -> RuntimeOwnership:
    schema = payload.get("schema")
    if schema != _RUNTIME_STATE_SCHEMA:
        raise RuntimeStateError(f"Unsupported runtime ownership schema: {schema!r}.")
    required = ("host", "subject", "backend", "backend_key", "version")
    if not all(isinstance(payload.get(name), str) and payload[name] for name in required):
        raise RuntimeStateError("Runtime ownership identity fields are malformed.")
    return RuntimeOwnership(
        host=str(payload["host"]),
        subject=str(payload["subject"]),
        backend=str(payload["backend"]),
        backend_key=str(payload["backend_key"]),
        version=str(payload["version"]),
        architecture=(
            str(payload["architecture"])
            if payload.get("architecture") not in (None, "")
            else None
        ),
        flavor=(
            str(payload["flavor"])
            if payload.get("flavor") not in (None, "")
            else None
        ),
        distribution=(
            str(payload["distribution"])
            if payload.get("distribution") not in (None, "")
            else None
        ),
        executable=(
            Path(str(payload["executable"]))
            if payload.get("executable") not in (None, "")
            else None
        ),
        prefix=(
            Path(str(payload["prefix"]))
            if payload.get("prefix") not in (None, "")
            else None
        ),
        schema=_RUNTIME_STATE_SCHEMA,
    )


def read_runtime_ownerships(
    context: OperationContext,
    subject: str,
) -> tuple[RuntimeOwnership, ...]:
    """Read all canonical runtime ownership records for one subject on this host."""
    root = _subject_state_root(context, subject)
    if not root.is_dir():
        return ()
    states: list[RuntimeOwnership] = []
    for path in sorted(root.glob("*/*.json")):
        payload = read_json_state(path)
        if payload is None:
            continue
        state = _ownership_from_payload(payload)
        if state.host != context.host or state.subject != subject:
            raise RuntimeStateError("Runtime ownership path and payload identity disagree.")
        expected = runtime_ownership_path(
            context,
            state.subject,
            state.backend,
            state.backend_key,
        )
        if path != expected:
            raise RuntimeStateError("Runtime ownership payload is stored under the wrong identity key.")
        states.append(state)
    return tuple(states)


def _write_runtime_ownership(
    context: OperationContext,
    state: RuntimeOwnership,
) -> None:
    write_json_state(
        runtime_ownership_path(
            context,
            state.subject,
            state.backend,
            state.backend_key,
        ),
        state.to_dict(),
    )


def _delete_runtime_ownership(
    context: OperationContext,
    state: RuntimeOwnership,
) -> None:
    path = runtime_ownership_path(
        context,
        state.subject,
        state.backend,
        state.backend_key,
    )
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _validate_backend_identity(
    backend: RuntimeBackend,
    desired: RuntimeDesiredState | None = None,
) -> OperationResult | None:
    if not backend.subject.strip() or not backend.name.strip():
        return OperationResult.error(
            "runtime_backend_identity_invalid",
            "Runtime backend subject/name cannot be empty.",
        )
    if desired is not None and (
        desired.subject != backend.subject or desired.backend != backend.name
    ):
        return OperationResult.error(
            "runtime_backend_desired_state_mismatch",
            "Desired runtime state does not target the supplied backend.",
            data={
                "backend_subject": backend.subject,
                "backend": backend.name,
                "desired": desired.to_dict(),
            },
        )
    return None


def _discover_exact(
    backend: RuntimeBackend,
    context: OperationContext,
) -> tuple[tuple[RuntimeInstance, ...], OperationResult | None]:
    try:
        instances = tuple(backend.discover(context))
    except Exception as exc:
        return (), OperationResult.error(
            "runtime_discovery_failed",
            f"Runtime backend discovery failed: {exc}",
        )

    keys: set[str] = set()
    for instance in instances:
        if instance.subject != backend.subject:
            return (), OperationResult.error(
                "runtime_discovery_identity_invalid",
                "Runtime backend returned an instance for a different subject.",
                data={"instance": instance.to_dict()},
            )
        if instance.backend == backend.name:
            if instance.backend_key in keys:
                return (), OperationResult.failure(
                    "runtime_discovery_ambiguous",
                    "Runtime backend returned duplicate exact backend keys.",
                    data={
                        "backend": backend.name,
                        "backend_key": instance.backend_key,
                        "instances": [item.to_dict() for item in instances],
                    },
                )
            keys.add(instance.backend_key)
    return instances, None


def _owned_backend_guard(
    context: OperationContext,
    subject: str,
    backend_name: str,
) -> tuple[tuple[RuntimeOwnership, ...], OperationResult | None]:
    try:
        ownerships = read_runtime_ownerships(context, subject)
    except (RuntimeStateError, ValueError) as exc:
        return (), OperationResult.error(
            "runtime_provenance_invalid",
            str(exc),
        )
    foreign = [state for state in ownerships if state.backend != backend_name]
    if foreign:
        return ownerships, OperationResult.failure(
            "runtime_backend_migration_required",
            "Machine-Soul already owns this runtime subject through another backend; explicit migration is required.",
            data={
                "subject": subject,
                "requested_backend": backend_name,
                "owned_backends": sorted({state.backend for state in foreign}),
                "foreign_ownership": [state.to_dict() for state in foreign],
            },
        )
    return ownerships, None


def adopt_runtime_instance(
    context: OperationContext,
    backend: RuntimeBackend,
    backend_key: str,
) -> OperationResult:
    """Explicitly adopt one exact pre-existing runtime instance."""
    invalid = _validate_backend_identity(backend)
    if invalid is not None:
        return invalid
    ownerships, guard = _owned_backend_guard(context, backend.subject, backend.name)
    if guard is not None:
        return guard
    instances, error = _discover_exact(backend, context)
    if error is not None:
        return error

    matches = [
        item
        for item in instances
        if item.backend == backend.name and item.backend_key == backend_key
    ]
    if len(matches) != 1:
        return OperationResult.failure(
            "runtime_instance_not_unique",
            "Runtime adoption requires exactly one matching backend instance.",
            data={
                "backend_key": backend_key,
                "matches": [item.to_dict() for item in matches],
            },
        )
    instance = matches[0]
    existing = next(
        (state for state in ownerships if state.backend_key == backend_key),
        None,
    )
    if existing is not None:
        if not existing.matches_instance(instance):
            return OperationResult.failure(
                "runtime_provenance_mismatch",
                "Owned runtime provenance no longer matches the discovered exact instance.",
                data={
                    "ownership": existing.to_dict(),
                    "instance": instance.to_dict(),
                },
            )
        return OperationResult.success(
            "runtime_instance_adopted",
            "Runtime instance is already owned by Machine-Soul.",
            data={"instance": instance.to_dict()},
        )

    if context.dry_run:
        return OperationResult.success(
            "would_adopt_runtime_instance",
            "Runtime instance would be explicitly adopted.",
            data={"instance": instance.to_dict()},
        )

    _write_runtime_ownership(
        context,
        RuntimeOwnership.from_instance(context.host, instance),
    )
    return OperationResult.success(
        "runtime_instance_adopted",
        "Runtime instance was explicitly adopted.",
        changed=True,
        data={"instance": instance.to_dict()},
    )


def _backend_result_failed(result: OperationResult) -> bool:
    return result.status is not ResultStatus.SUCCESS


def _selection_result(
    backend: RuntimeBackend,
    context: OperationContext,
) -> tuple[str | None, OperationResult | None]:
    try:
        return backend.selected_key(context), None
    except Exception as exc:
        return None, OperationResult.error(
            "runtime_selection_discovery_failed",
            f"Runtime backend selected/default discovery failed: {exc}",
        )


def reconcile_runtime(
    context: OperationContext,
    backend: RuntimeBackend,
    desired: RuntimeDesiredState,
) -> OperationResult:
    """Reconcile exact owned runtime instances and selected/default state."""
    invalid = _validate_backend_identity(backend, desired)
    if invalid is not None:
        return invalid

    ownerships, guard = _owned_backend_guard(context, desired.subject, backend.name)
    if guard is not None:
        return guard

    instances, error = _discover_exact(backend, context)
    if error is not None:
        return error
    selected_before, error = _selection_result(backend, context)
    if error is not None:
        return error

    managed_observed = {
        item.backend_key: item
        for item in instances
        if item.backend == backend.name
    }
    ownership_by_key = {state.backend_key: state for state in ownerships}
    desired_by_key = {spec.backend_key: spec for spec in desired.instances}

    mismatched = [
        {
            "ownership": ownership.to_dict(),
            "instance": managed_observed[key].to_dict(),
        }
        for key, ownership in ownership_by_key.items()
        if key in managed_observed
        and not ownership.matches_instance(managed_observed[key])
    ]
    if mismatched:
        return OperationResult.failure(
            "runtime_provenance_mismatch",
            "Owned runtime provenance does not match current exact discovery.",
            data={"mismatches": mismatched},
        )

    unmanaged_desired = [
        managed_observed[key]
        for key in desired_by_key
        if key in managed_observed and key not in ownership_by_key
    ]
    if unmanaged_desired:
        return OperationResult.failure(
            "runtime_unmanaged_conflict",
            "Desired runtime instances already exist but are not owned; explicit adoption is required.",
            data={"instances": [item.to_dict() for item in unmanaged_desired]},
        )

    removal_keys = set(ownership_by_key) - set(desired_by_key)
    if selected_before in removal_keys and desired.selected_key is None:
        return OperationResult.failure(
            "runtime_selected_removal_requires_reselection",
            "The currently selected owned runtime would be removed without a replacement selection.",
            data={
                "selected_key": selected_before,
                "removal_keys": sorted(removal_keys),
            },
        )

    if context.dry_run:
        return OperationResult.success(
            "would_reconcile_runtime",
            "Runtime desired set and selected/default state would be reconciled.",
            data={
                "desired": desired.to_dict(),
                "selected_before": selected_before,
                "install_keys": sorted(set(desired_by_key) - set(managed_observed)),
                "remove_keys": sorted(removal_keys),
                "select_key": (
                    desired.selected_key
                    if desired.selected_key != selected_before
                    else None
                ),
                "owned_keys": sorted(ownership_by_key),
                "observed_instances": [item.to_dict() for item in instances],
            },
        )

    changed = False
    actions: list[dict[str, object]] = []

    # Install first so a replacement selection can exist before any removal.
    for key in sorted(set(desired_by_key) - set(managed_observed)):
        spec = desired_by_key[key]
        result = backend.install(context, spec)
        actions.append({"action": "install", "backend_key": key, "result": result.to_dict()})
        changed = changed or result.changed
        if _backend_result_failed(result):
            return OperationResult.error(
                "runtime_install_failed",
                f"Runtime backend failed to install {key!r}.",
                changed=changed,
                data={"actions": actions, "backend_result": result.to_dict()},
            )
        observed_after, discovery_error = _discover_exact(backend, context)
        if discovery_error is not None:
            return OperationResult.error(
                "runtime_verification_failed",
                "Runtime installation succeeded but rediscovery failed.",
                changed=True,
                data={"actions": actions, "discovery": discovery_error.to_dict()},
            )
        matches = [
            item
            for item in observed_after
            if item.backend == backend.name and item.backend_key == key
        ]
        if len(matches) != 1:
            return OperationResult.error(
                "runtime_verification_failed",
                "Runtime installation returned success but the exact instance was not discovered uniquely.",
                changed=True,
                data={"actions": actions, "backend_key": key},
            )
        _write_runtime_ownership(
            context,
            RuntimeOwnership.from_instance(context.host, matches[0]),
        )
        ownership_by_key[key] = RuntimeOwnership.from_instance(context.host, matches[0])
        managed_observed[key] = matches[0]
        changed = True

    selected_now, selection_error = _selection_result(backend, context)
    if selection_error is not None:
        return OperationResult.error(
            "runtime_selection_discovery_failed",
            selection_error.message,
            changed=changed,
            data={"actions": actions},
        )

    if desired.selected_key is not None and desired.selected_key != selected_now:
        selected_instance = managed_observed.get(desired.selected_key)
        if selected_instance is None:
            return OperationResult.error(
                "runtime_selection_target_missing",
                "Desired selected runtime is not installed after installation reconciliation.",
                changed=changed,
                data={"selected_key": desired.selected_key, "actions": actions},
            )
        result = backend.select(context, selected_instance)
        actions.append(
            {
                "action": "select",
                "backend_key": desired.selected_key,
                "result": result.to_dict(),
            }
        )
        changed = changed or result.changed
        if _backend_result_failed(result):
            return OperationResult.error(
                "runtime_selection_failed",
                "Runtime backend failed to reconcile selected/default state.",
                changed=changed,
                data={"actions": actions, "backend_result": result.to_dict()},
            )
        selected_now, selection_error = _selection_result(backend, context)
        if selection_error is not None or selected_now != desired.selected_key:
            return OperationResult.error(
                "runtime_selection_verification_failed",
                "Runtime backend selection mutation did not verify.",
                changed=True,
                data={
                    "actions": actions,
                    "selected_expected": desired.selected_key,
                    "selected_observed": selected_now,
                },
            )
        changed = True

    for key in sorted(removal_keys):
        ownership = ownership_by_key[key]
        instance = managed_observed.get(key)
        if instance is None:
            _delete_runtime_ownership(context, ownership)
            actions.append({"action": "clear_stale_ownership", "backend_key": key})
            changed = True
            continue
        result = backend.uninstall(context, instance)
        actions.append({"action": "uninstall", "backend_key": key, "result": result.to_dict()})
        changed = changed or result.changed
        if _backend_result_failed(result):
            return OperationResult.error(
                "runtime_uninstall_failed",
                f"Runtime backend failed to uninstall {key!r}.",
                changed=changed,
                data={"actions": actions, "backend_result": result.to_dict()},
            )
        observed_after, discovery_error = _discover_exact(backend, context)
        if discovery_error is not None:
            return OperationResult.error(
                "runtime_verification_failed",
                "Runtime uninstall succeeded but rediscovery failed.",
                changed=True,
                data={"actions": actions, "discovery": discovery_error.to_dict()},
            )
        if any(
            item.backend == backend.name and item.backend_key == key
            for item in observed_after
        ):
            return OperationResult.error(
                "runtime_verification_failed",
                "Runtime uninstall returned success but the exact instance is still present.",
                changed=True,
                data={"actions": actions, "backend_key": key},
            )
        _delete_runtime_ownership(context, ownership)
        ownership_by_key.pop(key, None)
        managed_observed.pop(key, None)
        changed = True

    final_instances, final_error = _discover_exact(backend, context)
    if final_error is not None:
        return OperationResult.error(
            "runtime_verification_failed",
            "Final runtime rediscovery failed.",
            changed=changed,
            data={"actions": actions, "discovery": final_error.to_dict()},
        )
    final_map = {
        item.backend_key: item
        for item in final_instances
        if item.backend == backend.name
    }
    missing = set(desired_by_key) - set(final_map)
    owned_extra = set(ownership_by_key) - set(desired_by_key)
    final_selected, selection_error = _selection_result(backend, context)
    if selection_error is not None:
        return OperationResult.error(
            "runtime_selection_discovery_failed",
            selection_error.message,
            changed=changed,
            data={"actions": actions},
        )
    if missing or owned_extra or (
        desired.selected_key is not None
        and final_selected != desired.selected_key
    ):
        return OperationResult.error(
            "runtime_verification_failed",
            "Runtime reconciliation did not converge to the desired owned state.",
            changed=changed,
            data={
                "actions": actions,
                "missing_keys": sorted(missing),
                "owned_extra_keys": sorted(owned_extra),
                "selected_expected": desired.selected_key,
                "selected_observed": final_selected,
            },
        )

    return OperationResult.success(
        "runtime_reconciled",
        "Runtime installed set and selected/default state are reconciled.",
        changed=changed,
        data={
            "actions": actions,
            "desired": desired.to_dict(),
            "selected_before": selected_before,
            "selected_after": final_selected,
            "instances": [item.to_dict() for item in final_instances],
            "owned_keys": sorted(ownership_by_key),
        },
    )
