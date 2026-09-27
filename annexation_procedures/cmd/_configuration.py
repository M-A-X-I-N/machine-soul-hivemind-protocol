"""CMD-specific AutoRun coupling around the generic config lifecycle."""

from __future__ import annotations

from typing import Mapping

from accumulated_instruments.machine_soul.model import (
    Application,
    ConflictPolicy,
    Operation,
    OperationContext,
    OperationResult,
    PlatformDeclaration,
)
from accumulated_instruments.machine_soul.operations.configuration import (
    apply_config,
    check_config,
    unapply_config,
)
from accumulated_instruments.machine_soul.state import (
    application_state_path,
    read_json_state,
    write_json_state,
)


def _registry_subkey(context: OperationContext) -> str:
    override = context.environment.get("MACHINE_SOUL_CMD_REGISTRY_KEY")
    if not override:
        return r"Software\Microsoft\Command Processor"

    prefix = "HKCU:\\"
    if not override.upper().startswith(prefix.upper()):
        raise ValueError("CMD registry override must target HKCU.")
    return override[len(prefix):].replace("/", "\\")


def _read_autorun(context: OperationContext) -> str | None:
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _registry_subkey(context)) as key:
            value, _ = winreg.QueryValueEx(key, "AutoRun")
            return str(value)
    except FileNotFoundError:
        return None


def _write_autorun(context: OperationContext, value: str) -> None:
    import winreg

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _registry_subkey(context)) as key:
        winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, value)


def _delete_autorun(context: OperationContext) -> None:
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _registry_subkey(context),
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            try:
                winreg.DeleteValue(key, "AutoRun")
            except FileNotFoundError:
                pass
    except FileNotFoundError:
        pass


def _expected_autorun(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
) -> tuple[str, OperationResult | None]:
    checked = check_config(application, declaration, context)
    # check_config always includes destination in data when resolution succeeds.
    destination = checked.data.get("destination")
    if not isinstance(destination, str):
        # A multi-target declaration would aggregate results; CMD intentionally
        # declares one linked command file.
        nested = checked.data.get("results")
        if isinstance(nested, list) and len(nested) == 1:
            candidate = nested[0]
            if isinstance(candidate, Mapping):
                data = candidate.get("data")
                if isinstance(data, Mapping) and isinstance(data.get("destination"), str):
                    destination = data["destination"]
    if not isinstance(destination, str):
        return "", checked
    return f'call "{destination}"', None


def handle_configuration(
    application: Application,
    declaration: PlatformDeclaration,
    operation: Operation,
    context: OperationContext,
) -> OperationResult:
    """Coordinate CMD's managed command file with HKCU AutoRun."""
    if context.platform.value != "windows":
        return OperationResult.unsupported(
            "platform_unsupported",
            "CMD configuration integration is Windows-only.",
        )

    expected, error = _expected_autorun(application, declaration, context)
    if error is not None and error.code in {
        "configuration_not_available",
        "configuration_not_declared",
    }:
        return error

    try:
        current = _read_autorun(context)
    except (OSError, ValueError) as exc:
        return OperationResult.error("registry_read_failed", str(exc))

    file_result = check_config(application, declaration, context)
    state_path = application_state_path(context, application.id, "autorun")
    legacy_state_path = (
        context.repository_root
        / "scratch"
        / "state"
        / "cmd"
        / context.host
        / context.target_account.name
        / "autorun.json"
    )
    saved = read_json_state(state_path)
    active_state_path = state_path
    if saved is None:
        saved = read_json_state(legacy_state_path)
        if saved is not None:
            active_state_path = legacy_state_path

    if operation is Operation.CHECK_CONFIG:
        if file_result.code == "applied" and current == expected:
            return OperationResult.success(
                "applied",
                "CMD command file and AutoRun integration are applied.",
                data={"autorun": expected},
            )
        if file_result.code == "not_applied" and current is None:
            return OperationResult.failure(
                "not_applied",
                "CMD configuration is not applied.",
            )
        return OperationResult.failure(
            "conflict",
            "CMD command file and AutoRun integration are not in one managed state.",
            data={"file_result": file_result.to_dict(), "current_autorun": current},
        )

    if operation is Operation.APPLY_CONFIG:
        if file_result.code == "applied" and current == expected:
            return OperationResult.success("applied", "CMD configuration is already applied.")

        if current is not None and current != expected:
            if context.conflict_policy is ConflictPolicy.ABORT:
                return OperationResult.failure(
                    "conflict",
                    "CMD AutoRun contains unmanaged state.",
                )
            if context.conflict_policy is ConflictPolicy.PROMPT:
                return OperationResult.failure(
                    "confirmation_required",
                    "CMD AutoRun replacement requires caller confirmation.",
                )

        if context.dry_run:
            return OperationResult.success(
                "would_apply",
                "CMD command file and AutoRun integration would be applied.",
            )

        prior = None if current == expected else current
        linked = apply_config(application, declaration, context)
        if linked.status.value != "success":
            return linked

        try:
            _write_autorun(context, expected)
            if _read_autorun(context) != expected:
                raise RuntimeError("CMD AutoRun verification failed.")
            if saved is None:
                write_json_state(
                    state_path,
                    {
                        "schema": 1,
                        "had_prior_autorun": prior is not None,
                        "prior_autorun": prior,
                        "expected_autorun": expected,
                    },
                )
        except Exception as exc:
            rollback = unapply_config(application, declaration, context)
            return OperationResult.error(
                "registry_apply_failed",
                f"CMD AutoRun mutation failed: {exc}",
                changed=(linked.changed and rollback.status.value != "success"),
                data={"rollback": rollback.to_dict()},
            )

        return OperationResult.success(
            "applied",
            "CMD command file and AutoRun integration were applied.",
            changed=(linked.changed or current != expected),
        )

    if operation is Operation.UNAPPLY_CONFIG:
        if file_result.code == "not_applied" and current is None:
            return OperationResult.success("not_applied", "CMD configuration is already not applied.")
        if current != expected:
            return OperationResult.failure(
                "conflict",
                "CMD AutoRun is no longer the managed value; refusing to overwrite it.",
            )
        if context.dry_run:
            return OperationResult.success(
                "would_unapply",
                "CMD command file and AutoRun integration would be unapplied.",
            )

        try:
            if saved and bool(saved.get("had_prior_autorun")):
                prior = saved.get("prior_autorun")
                if not isinstance(prior, str):
                    raise RuntimeError("Recorded prior CMD AutoRun value is invalid.")
                _write_autorun(context, prior)
            else:
                _delete_autorun(context)
        except Exception as exc:
            return OperationResult.error("registry_restore_failed", str(exc))

        unlinked = unapply_config(application, declaration, context)
        if unlinked.status.value != "success":
            try:
                _write_autorun(context, expected)
            except Exception:
                return OperationResult.error(
                    "rollback_failed",
                    "CMD file unapply failed and managed AutoRun could not be restored.",
                    changed=True,
                    data={"file_result": unlinked.to_dict()},
                )
            return unlinked

        try:
            active_state_path.unlink()
        except FileNotFoundError:
            pass

        return OperationResult.success(
            "not_applied",
            "CMD command file and AutoRun integration were unapplied.",
            changed=True,
        )

    raise ValueError(f"Unsupported CMD configuration operation: {operation!r}")
