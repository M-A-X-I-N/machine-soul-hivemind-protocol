"""Generic safe configuration operation engines."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import shutil

from ..configuration import ConfigurationResolutionError, ResolvedConfiguration, resolve_configurations
from ..filesystem import (
    LinkInfo,
    LinkStatus,
    canonical_target,
    classify_link,
    create_file_symlink,
    paths_equal,
)
from ..model import (
    Application,
    ConflictPolicy,
    OperationContext,
    OperationResult,
    PlatformDeclaration,
)
from ..state import (
    ConfigState,
    backup_root,
    delete_config_state,
    read_config_state,
    resolve_backup_path,
    write_config_state,
)


def _result_data(target: ResolvedConfiguration) -> dict[str, object]:
    return {
        "configuration": target.configuration.name,
        "source": str(target.source),
        "destination": str(target.destination),
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_relative(context: OperationContext, source: Path) -> str:
    try:
        return str(source.relative_to(context.repository_root))
    except ValueError:
        return str(source)


def _backup_relative(context: OperationContext, backup: Path | None) -> str | None:
    if backup is None:
        return None
    try:
        return str(backup.relative_to(context.repository_root))
    except ValueError:
        return None


def _check_one(target: ResolvedConfiguration) -> OperationResult:
    info = classify_link(target.source, target.destination)
    data = _result_data(target)
    if info.actual_target is not None:
        data["actual_target"] = str(info.actual_target)

    if info.status is LinkStatus.APPLIED:
        return OperationResult.success("applied", "Configuration is applied.", data=data)
    if info.status is LinkStatus.NOT_APPLIED:
        return OperationResult.failure("not_applied", "Configuration is not applied.", data=data)
    if info.status is LinkStatus.CONFLICT:
        return OperationResult.failure("conflict", "Destination contains unmanaged state.", data=data)
    if info.status is LinkStatus.WRONG_TARGET:
        return OperationResult.failure("wrong_target", "Destination symlink targets another object.", data=data)
    return OperationResult.failure("broken", "Destination symlink target does not exist.", data=data)


def _restore_prior(
    *,
    destination: Path,
    prior_type: str,
    backup: Path | None,
    prior_target: str | None,
) -> None:
    if os.path.lexists(destination):
        if destination.is_dir() and not destination.is_symlink():
            raise RuntimeError("Rollback destination unexpectedly became a directory.")
        destination.unlink()

    if prior_type == "file":
        if backup is None or not backup.is_file():
            raise RuntimeError("Recorded backup is missing during rollback.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(backup), str(destination))
    elif prior_type == "symlink":
        if prior_target is None:
            raise RuntimeError("Prior symlink target is missing during rollback.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(prior_target, destination, target_is_directory=False)
    elif prior_type != "absent":
        raise RuntimeError(f"Unknown prior object type: {prior_type!r}.")


def _repair_relocated(
    application: Application,
    context: OperationContext,
    target: ResolvedConfiguration,
    info: LinkInfo,
) -> OperationResult | None:
    if info.status not in {LinkStatus.WRONG_TARGET, LinkStatus.BROKEN}:
        return None
    if info.actual_target is None or info.raw_target is None:
        return None

    state = read_config_state(context, application.id, target.destination)
    if state is None:
        return None

    logical_source = context.repository_root / state.source_relative
    if not paths_equal(info.actual_target, state.applied_target):
        return None
    if not paths_equal(canonical_target(logical_source), canonical_target(target.source)):
        return None

    data = _result_data(target)
    if context.dry_run:
        data["action"] = "repair_relocated_link"
        return OperationResult.success(
            "would_repair_relocated",
            "Managed stale link would be repaired for the relocated checkout.",
            data=data,
        )

    destination = info.destination
    destination.unlink()
    try:
        create_file_symlink(target.source, destination)
        verified = classify_link(target.source, destination)
        if verified.status is not LinkStatus.APPLIED:
            raise RuntimeError(f"Relocated link verification returned {verified.status.value}.")
    except Exception as exc:
        try:
            if os.path.lexists(destination):
                destination.unlink()
            os.symlink(info.raw_target, destination, target_is_directory=False)
        except Exception as rollback_exc:
            return OperationResult.error(
                "rollback_failed",
                f"Relocation repair failed and rollback also failed: {rollback_exc}",
                changed=True,
                data=data,
            )
        return OperationResult.error(
            "relocation_repair_failed",
            f"Relocation repair failed: {exc}",
            data=data,
        )

    updated = ConfigState(
        application=state.application,
        host=state.host,
        account=state.account,
        source_relative=state.source_relative,
        destination=state.destination,
        prior_type=state.prior_type,
        backup_relative=state.backup_relative,
        backup_absolute=state.backup_absolute,
        prior_target=state.prior_target,
        applied_target=str(canonical_target(target.source)),
        applied_utc=_now(),
    )
    try:
        write_config_state(context, updated)
    except Exception as exc:
        # The link itself is valid and owned, so truthfully report a partial
        # change rather than pretending the state update succeeded.
        return OperationResult.error(
            "state_write_failed",
            f"Relocated link was repaired but deployment state could not be updated: {exc}",
            changed=True,
            data=data,
        )

    return OperationResult.success(
        "applied",
        "Managed link was repaired for the relocated checkout.",
        changed=True,
        data=data,
    )


def _apply_one(
    application: Application,
    context: OperationContext,
    target: ResolvedConfiguration,
) -> OperationResult:
    info = classify_link(target.source, target.destination)
    data = _result_data(target)

    if info.status is LinkStatus.APPLIED:
        return OperationResult.success("applied", "Configuration is already applied.", data=data)

    repaired = _repair_relocated(application, context, target, info)
    if repaired is not None:
        return repaired

    destination = info.destination
    if destination.is_dir() and not destination.is_symlink():
        return OperationResult.failure(
            "conflict_directory",
            "Destination is a directory and cannot be replaced as a managed config file.",
            data=data,
        )

    if info.status is not LinkStatus.NOT_APPLIED:
        if context.conflict_policy is ConflictPolicy.ABORT:
            return OperationResult.failure(
                "conflict",
                "Existing unmanaged destination requires an explicit replacement policy.",
                data=data,
            )
        if context.conflict_policy is ConflictPolicy.PROMPT:
            return OperationResult.failure(
                "confirmation_required",
                "Existing unmanaged destination requires caller confirmation.",
                data=data,
            )

    if context.dry_run:
        data["action"] = (
            "create_link"
            if info.status is LinkStatus.NOT_APPLIED
            else "backup_and_replace"
        )
        return OperationResult.success(
            "would_apply",
            "Configuration would be applied.",
            data=data,
        )

    prior_type = "absent"
    prior_target: str | None = None
    backup: Path | None = None

    if info.status is not LinkStatus.NOT_APPLIED:
        if destination.is_symlink():
            prior_type = "symlink"
            prior_target = os.readlink(destination)
            destination.unlink()
        elif destination.is_file():
            prior_type = "file"
            directory = backup_root(context, application.id, destination)
            directory.mkdir(parents=True, exist_ok=False)
            backup = directory / "original"
            shutil.move(str(destination), str(backup))
        else:
            return OperationResult.failure(
                "unsupported_destination_type",
                "Destination exists as an unsupported filesystem object.",
                data=data,
            )

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        create_file_symlink(target.source, destination)
        verified = classify_link(target.source, destination)
        if verified.status is not LinkStatus.APPLIED:
            raise RuntimeError(f"Symlink verification returned {verified.status.value}.")
    except Exception as exc:
        try:
            _restore_prior(
                destination=destination,
                prior_type=prior_type,
                backup=backup,
                prior_target=prior_target,
            )
        except Exception as rollback_exc:
            return OperationResult.error(
                "rollback_failed",
                f"Apply failed ({exc}) and rollback failed ({rollback_exc}).",
                changed=True,
                data=data,
            )
        return OperationResult.error(
            "apply_failed",
            f"Configuration apply failed and was rolled back: {exc}",
            data=data,
        )

    state = ConfigState(
        application=application.id,
        host=context.host,
        account=context.target_account.name,
        source_relative=_source_relative(context, target.source),
        destination=str(destination),
        prior_type=prior_type,
        backup_relative=_backup_relative(context, backup),
        backup_absolute=(str(backup) if backup is not None else None),
        prior_target=prior_target,
        applied_target=str(canonical_target(target.source)),
        applied_utc=_now(),
    )
    try:
        write_config_state(context, state)
    except Exception as exc:
        try:
            _restore_prior(
                destination=destination,
                prior_type=prior_type,
                backup=backup,
                prior_target=prior_target,
            )
        except Exception as rollback_exc:
            return OperationResult.error(
                "rollback_failed",
                f"State write failed ({exc}) and rollback failed ({rollback_exc}).",
                changed=True,
                data=data,
            )
        return OperationResult.error(
            "state_write_failed",
            f"State write failed and configuration was rolled back: {exc}",
            data=data,
        )

    return OperationResult.success(
        "applied",
        "Configuration was applied.",
        changed=True,
        data=data,
    )


def _unapply_one(
    application: Application,
    context: OperationContext,
    target: ResolvedConfiguration,
) -> OperationResult:
    info = classify_link(target.source, target.destination)
    data = _result_data(target)

    if info.status is LinkStatus.NOT_APPLIED:
        return OperationResult.success("not_applied", "Configuration is already not applied.", data=data)

    if info.status is not LinkStatus.APPLIED:
        return OperationResult.failure(
            "conflict",
            "Destination is not the expected managed symlink; refusing to remove it.",
            data=data,
        )

    state = read_config_state(context, application.id, target.destination)
    if state is None:
        return OperationResult.failure(
            "ownership_unproven",
            "Expected symlink exists but no Machine-Soul ownership state was found.",
            data=data,
        )
    if not paths_equal(info.actual_target or "", state.applied_target):
        return OperationResult.failure(
            "ownership_conflict",
            "Deployment state does not match the currently managed symlink target.",
            data=data,
        )

    if context.dry_run:
        data["action"] = "unapply_and_restore"
        return OperationResult.success(
            "would_unapply",
            "Configuration would be unapplied and prior state restored when recorded.",
            data=data,
        )

    backup = resolve_backup_path(context, state)
    destination = info.destination
    destination.unlink()

    try:
        _restore_prior(
            destination=destination,
            prior_type=state.prior_type,
            backup=backup,
            prior_target=state.prior_target,
        )
    except Exception as exc:
        # Try to restore the managed link so ownership/safety is not silently
        # lost just because restoration failed.
        try:
            if os.path.lexists(destination):
                if destination.is_dir() and not destination.is_symlink():
                    raise RuntimeError("Destination became a directory during failed restoration.")
                destination.unlink()
            destination.parent.mkdir(parents=True, exist_ok=True)
            create_file_symlink(target.source, destination)
            changed = False
        except Exception:
            changed = True
        return OperationResult.error(
            "restore_failed",
            f"Prior-state restoration failed: {exc}",
            changed=changed,
            data=data,
        )

    delete_config_state(context, application.id, destination)
    return OperationResult.success(
        "not_applied",
        "Configuration was unapplied.",
        changed=True,
        data=data,
    )


def _resolve(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> tuple[ResolvedConfiguration, ...] | OperationResult:
    try:
        targets = resolve_configurations(context, application, declaration)
    except ConfigurationResolutionError as exc:
        return OperationResult.unsupported(
            "configuration_not_available",
            str(exc),
            data={"application": application.id},
        )
    if not targets:
        return OperationResult.unsupported(
            "configuration_not_declared",
            "Application declares no configuration files for this platform.",
            data={"application": application.id},
        )
    return targets


def _aggregate(operation: str, results: list[OperationResult]) -> OperationResult:
    if len(results) == 1:
        return results[0]

    changed = any(result.changed for result in results)
    payload = [result.to_dict() for result in results]
    if all(result.status.value == "success" for result in results):
        code = {
            "check": "applied",
            "apply": "applied",
            "unapply": "not_applied",
        }[operation]
        return OperationResult.success(
            code,
            f"All {len(results)} configuration targets completed successfully.",
            changed=changed,
            data={"results": payload},
        )

    return OperationResult.failure(
        "configuration_mixed",
        "Configuration targets produced mixed/non-success outcomes.",
        changed=changed,
        data={"results": payload},
    )


def check_config(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> OperationResult:
    targets = _resolve(application, declaration, context)
    if isinstance(targets, OperationResult):
        return targets
    return _aggregate("check", [_check_one(target) for target in targets])


def apply_config(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> OperationResult:
    targets = _resolve(application, declaration, context)
    if isinstance(targets, OperationResult):
        return targets

    completed: list[tuple[ResolvedConfiguration, OperationResult]] = []
    for target in targets:
        result = _apply_one(application, context, target)
        completed.append((target, result))
        if result.status.value != "success":
            changed_targets = [
                previous_target
                for previous_target, previous_result in completed[:-1]
                if previous_result.changed
            ]
            rollback_failures: list[dict[str, object]] = []
            for previous in reversed(changed_targets):
                rollback = _unapply_one(application, context, previous)
                if rollback.status.value != "success":
                    rollback_failures.append(rollback.to_dict())
            if rollback_failures:
                return OperationResult.error(
                    "rollback_failed",
                    "Multi-file apply failed and one or more earlier targets could not be rolled back.",
                    changed=True,
                    data={
                        "failed_result": result.to_dict(),
                        "rollback_failures": rollback_failures,
                    },
                )
            return result

    return _aggregate("apply", [result for _, result in completed])


def unapply_config(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> OperationResult:
    targets = _resolve(application, declaration, context)
    if isinstance(targets, OperationResult):
        return targets

    # Reverse order mirrors apply for applications declaring multiple related
    # config files while keeping each target's own restoration transaction.
    results = [_unapply_one(application, context, target) for target in reversed(targets)]
    results.reverse()
    return _aggregate("unapply", results)
