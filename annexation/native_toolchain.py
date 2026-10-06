"""Windows Visual Studio/Build Tools native-toolchain discovery and ownership."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Callable, Iterable

from .model import (
    NativeToolchainOwnership,
    NativeToolchainRequirement,
    OperationContext,
    OperationResult,
    Platform,
    VisualStudioInstance,
)
from .process import ProcessResult, run_process
from .state import read_json_state, write_json_state


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]
VersionLister = Callable[[Path], Iterable[str]]

_STATE_SCHEMA = 1
_SUCCESS_RESTART_REQUIRED = 3010
_SUCCESS_REBOOT_INITIATED = 1641


class NativeToolchainDiscoveryError(RuntimeError):
    """Visual Studio setup discovery could not produce trustworthy state."""


def _default_which(command: str) -> str | None:
    return shutil.which(command)


def _default_msvc_versions(installation_path: Path) -> tuple[str, ...]:
    root = installation_path / "VC" / "Tools" / "MSVC"
    try:
        return tuple(sorted(item.name for item in root.iterdir() if item.is_dir()))
    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
        return ()


def resolve_vswhere_path(
    *,
    which: Which = _default_which,
    environ: dict[str, str] | None = None,
) -> str | None:
    """Resolve vswhere without relying only on ambient PATH."""
    located = which("vswhere")
    if located:
        return located

    environment = environ if environ is not None else os.environ
    program_files_x86 = environment.get("ProgramFiles(x86)")
    if not program_files_x86:
        return None
    candidate = (
        Path(program_files_x86)
        / "Microsoft Visual Studio"
        / "Installer"
        / "vswhere.exe"
    )
    return str(candidate) if candidate.is_file() else None


def _package_ids(payload: object) -> frozenset[str]:
    if not isinstance(payload, list):
        return frozenset()
    package_ids = []
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            package_ids.append(item["id"])
    return frozenset(package_ids)


def discover_visual_studio_instances(
    *,
    runner: Runner = run_process,
    vswhere_path: str | None = None,
    which: Which = _default_which,
    environ: dict[str, str] | None = None,
    version_lister: VersionLister = _default_msvc_versions,
) -> tuple[VisualStudioInstance, ...]:
    """Discover exact modern Visual Studio/Build Tools setup instances."""
    resolved = vswhere_path or resolve_vswhere_path(which=which, environ=environ)
    if resolved is None:
        raise NativeToolchainDiscoveryError("vswhere is not available.")

    result = runner(
        [
            resolved,
            "-all",
            "-products",
            "*",
            "-format",
            "json",
            "-utf8",
            "-include",
            "packages",
        ]
    )
    if result.returncode != 0:
        raise NativeToolchainDiscoveryError(
            f"vswhere failed with exit code {result.returncode}: {result.stderr[-1000:]}"
        )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise NativeToolchainDiscoveryError("vswhere returned malformed JSON.") from exc
    if not isinstance(payload, list):
        raise NativeToolchainDiscoveryError("vswhere JSON root must be an array.")

    instances: list[VisualStudioInstance] = []
    seen: set[str] = set()
    for raw in payload:
        if not isinstance(raw, dict):
            raise NativeToolchainDiscoveryError("vswhere instance entry must be an object.")
        instance_id = raw.get("instanceId")
        installation_path = raw.get("installationPath")
        installation_version = raw.get("installationVersion")
        if not all(isinstance(value, str) and value.strip() for value in (
            instance_id,
            installation_path,
            installation_version,
        )):
            raise NativeToolchainDiscoveryError(
                "vswhere instance is missing instanceId, installationPath, or installationVersion."
            )
        if instance_id in seen:
            raise NativeToolchainDiscoveryError(
                f"vswhere returned duplicate instance ID {instance_id!r}."
            )
        seen.add(instance_id)

        catalog = raw.get("catalog") if isinstance(raw.get("catalog"), dict) else {}
        properties = raw.get("properties") if isinstance(raw.get("properties"), dict) else {}
        product_id = raw.get("productId")
        channel_id = raw.get("channelId") or properties.get("channelId")
        display_name = raw.get("displayName") or catalog.get("productDisplayVersion")

        path = Path(installation_path)
        instances.append(
            VisualStudioInstance(
                instance_id=instance_id,
                installation_path=path,
                installation_version=installation_version,
                product_id=(product_id if isinstance(product_id, str) else None),
                display_name=(display_name if isinstance(display_name, str) else None),
                channel_id=(channel_id if isinstance(channel_id, str) else None),
                is_complete=bool(raw.get("isComplete", False)),
                is_launchable=bool(raw.get("isLaunchable", False)),
                is_prerelease=bool(raw.get("isPrerelease", False)),
                component_ids=_package_ids(raw.get("packages")),
                msvc_versions=tuple(version_lister(path)),
            )
        )

    return tuple(sorted(instances, key=lambda item: item.instance_id.casefold()))


def _target_capability_present(instance: VisualStudioInstance, target: str) -> bool:
    ids = tuple(component.casefold() for component in instance.component_ids)
    if target in {"x86", "amd64"}:
        return any(".vc." in item and ".x86.x64" in item for item in ids)
    if target == "arm":
        return any(".vc." in item and ".arm" in item and ".arm64" not in item for item in ids)
    if target in {"arm64", "arm64ec"}:
        return any(".vc." in item and ".arm64" in item for item in ids)
    return False


def instance_satisfies_requirement(
    instance: VisualStudioInstance,
    requirement: NativeToolchainRequirement,
) -> bool:
    """Return whether one exact instance satisfies a native build capability query."""
    if not instance.is_complete:
        return False
    if instance.is_prerelease and not requirement.allow_prerelease:
        return False
    if not requirement.component_ids.issubset(instance.component_ids):
        return False
    if requirement.msvc_version_prefix is not None:
        if not any(
            version.startswith(requirement.msvc_version_prefix)
            for version in instance.msvc_versions
        ):
            return False
    if not _target_capability_present(instance, requirement.target_architecture):
        return False
    return True


def find_native_toolchain_candidates(
    requirement: NativeToolchainRequirement,
    instances: Iterable[VisualStudioInstance],
) -> tuple[VisualStudioInstance, ...]:
    """Find complete setup instances satisfying an explicit native requirement."""
    return tuple(
        instance
        for instance in instances
        if instance_satisfies_requirement(instance, requirement)
    )


def native_toolchain_state_path(
    context: OperationContext,
    instance_id: str,
) -> Path:
    """Return machine-scoped ownership state independent of target account."""
    if not instance_id.strip():
        raise ValueError("instance_id cannot be empty.")
    key = hashlib.sha256(instance_id.encode("utf-8")).hexdigest()
    return (
        context.repository_root
        / "scratch"
        / "state"
        / "native_toolchain"
        / context.host
        / "visual_studio"
        / f"{key}.json"
    )


def read_native_toolchain_ownership(
    context: OperationContext,
    instance_id: str,
) -> NativeToolchainOwnership | None:
    payload = read_json_state(native_toolchain_state_path(context, instance_id))
    if payload is None:
        return None
    schema = payload.get("schema")
    if schema != _STATE_SCHEMA:
        raise ValueError(f"Unsupported native toolchain state schema: {schema!r}.")
    if payload.get("host") != context.host:
        raise ValueError("Native toolchain ownership host does not match current host.")
    if payload.get("instance_id") != instance_id:
        raise ValueError("Native toolchain ownership instance ID does not match state key.")
    owned = payload.get("owned_components", [])
    if not isinstance(owned, list) or not all(isinstance(item, str) for item in owned):
        raise ValueError("Native toolchain owned_components must be a string array.")
    path = payload.get("installation_path")
    if not isinstance(path, str) or not path:
        raise ValueError("Native toolchain ownership installation_path is invalid.")
    return NativeToolchainOwnership(
        host=context.host,
        instance_id=instance_id,
        installation_path=Path(path),
        owned_components=frozenset(owned),
        schema=_STATE_SCHEMA,
    )


def _write_ownership(
    context: OperationContext,
    state: NativeToolchainOwnership,
) -> None:
    write_json_state(
        native_toolchain_state_path(context, state.instance_id),
        state.to_dict(),
    )


def _windows_guard(context: OperationContext) -> OperationResult | None:
    if context.platform is Platform.WINDOWS:
        return None
    return OperationResult.unsupported(
        "native_toolchain_platform_unsupported",
        "Visual Studio native toolchain ownership is only supported on Windows.",
    )


def adopt_visual_studio_instance(
    context: OperationContext,
    instance: VisualStudioInstance,
) -> OperationResult:
    """Explicitly adopt an existing setup instance as a component-ownership target."""
    guard = _windows_guard(context)
    if guard is not None:
        return guard
    if not instance.is_complete:
        return OperationResult.failure(
            "visual_studio_instance_incomplete",
            "Refusing to adopt an incomplete Visual Studio setup instance.",
            data={"instance": instance.to_dict()},
        )

    existing = read_native_toolchain_ownership(context, instance.instance_id)
    if existing is not None:
        if existing.installation_path != instance.installation_path:
            return OperationResult.failure(
                "visual_studio_instance_identity_mismatch",
                "The adopted instance ID now resolves to a different installation path.",
                data={
                    "instance": instance.to_dict(),
                    "owned_installation_path": str(existing.installation_path),
                },
            )
        return OperationResult.success(
            "visual_studio_instance_adopted",
            "Visual Studio setup instance is already adopted for component ownership.",
            data={
                "instance": instance.to_dict(),
                "owned_components": sorted(existing.owned_components),
            },
        )

    state = NativeToolchainOwnership(
        host=context.host,
        instance_id=instance.instance_id,
        installation_path=instance.installation_path,
    )
    if context.dry_run:
        return OperationResult.success(
            "would_adopt_visual_studio_instance",
            "Visual Studio setup instance would be adopted for component ownership.",
            data={"instance": instance.to_dict()},
        )
    _write_ownership(context, state)
    return OperationResult.success(
        "visual_studio_instance_adopted",
        "Visual Studio setup instance was adopted for component ownership.",
        changed=True,
        data={"instance": instance.to_dict(), "owned_components": []},
    )


def check_native_toolchain_requirement(
    context: OperationContext,
    requirement: NativeToolchainRequirement,
    *,
    runner: Runner = run_process,
    vswhere_path: str | None = None,
    which: Which = _default_which,
    environ: dict[str, str] | None = None,
    version_lister: VersionLister = _default_msvc_versions,
) -> OperationResult:
    """Report candidates satisfying one explicit compiler/component capability query."""
    guard = _windows_guard(context)
    if guard is not None:
        return guard
    try:
        instances = discover_visual_studio_instances(
            runner=runner,
            vswhere_path=vswhere_path,
            which=which,
            environ=environ,
            version_lister=version_lister,
        )
    except NativeToolchainDiscoveryError as exc:
        return OperationResult.error(
            "native_toolchain_discovery_failed",
            str(exc),
        )

    candidates = find_native_toolchain_candidates(requirement, instances)
    data = {
        "requirement": requirement.to_dict(),
        "candidates": [item.to_dict() for item in candidates],
        "instances": [item.to_dict() for item in instances],
    }
    if candidates:
        return OperationResult.success(
            "native_toolchain_requirement_satisfied",
            "At least one complete native toolchain instance satisfies the requirement.",
            data=data,
        )
    return OperationResult.failure(
        "native_toolchain_requirement_missing",
        "No complete native toolchain instance satisfies the requirement.",
        data=data,
    )


def _setup_path(
    *,
    setup_path: str | None,
    environ: dict[str, str] | None,
) -> str | None:
    if setup_path:
        return setup_path
    environment = environ if environ is not None else os.environ
    program_files_x86 = environment.get("ProgramFiles(x86)")
    if not program_files_x86:
        return None
    candidate = (
        Path(program_files_x86)
        / "Microsoft Visual Studio"
        / "Installer"
        / "setup.exe"
    )
    return str(candidate) if candidate.is_file() else None


def _find_instance(
    instances: Iterable[VisualStudioInstance],
    instance_id: str,
) -> VisualStudioInstance | None:
    matches = [item for item in instances if item.instance_id == instance_id]
    if len(matches) != 1:
        return None
    return matches[0]


def _installer_result(
    returncode: int,
    *,
    changed: bool,
    data: dict[str, object],
) -> OperationResult | None:
    if returncode == 0:
        return None
    if returncode in {_SUCCESS_RESTART_REQUIRED, _SUCCESS_REBOOT_INITIATED}:
        data["restart_required"] = True
        data["installer_returncode"] = returncode
        return None
    if returncode == 740:
        return OperationResult.error(
            "visual_studio_elevation_required",
            "Visual Studio Installer requires elevation.",
            changed=changed,
            data={**data, "installer_returncode": returncode},
        )
    if returncode in {1001, 1618}:
        code = "visual_studio_installer_busy"
    elif returncode in {1003, 8006}:
        code = "visual_studio_instance_in_use"
    elif returncode == 3010:
        code = "visual_studio_restart_required"
    else:
        code = "visual_studio_installer_failed"
    return OperationResult.error(
        code,
        f"Visual Studio Installer failed with exit code {returncode}.",
        changed=changed,
        data={**data, "installer_returncode": returncode},
    )


def reconcile_visual_studio_components(
    context: OperationContext,
    instance_id: str,
    desired_component_ids: Iterable[str],
    *,
    runner: Runner = run_process,
    vswhere_path: str | None = None,
    setup_path: str | None = None,
    which: Which = _default_which,
    environ: dict[str, str] | None = None,
    version_lister: VersionLister = _default_msvc_versions,
) -> OperationResult:
    """Conservatively reconcile exact owned components in one adopted setup instance."""
    guard = _windows_guard(context)
    if guard is not None:
        return guard
    desired = frozenset(
        str(item) for item in desired_component_ids if str(item).strip()
    )
    ownership = read_native_toolchain_ownership(context, instance_id)
    if ownership is None:
        return OperationResult.failure(
            "visual_studio_instance_not_adopted",
            "The Visual Studio setup instance must be explicitly adopted before mutation.",
            data={"instance_id": instance_id},
        )

    try:
        before_instances = discover_visual_studio_instances(
            runner=runner,
            vswhere_path=vswhere_path,
            which=which,
            environ=environ,
            version_lister=version_lister,
        )
    except NativeToolchainDiscoveryError as exc:
        return OperationResult.error("native_toolchain_discovery_failed", str(exc))

    before = _find_instance(before_instances, instance_id)
    if before is None:
        return OperationResult.failure(
            "visual_studio_instance_missing",
            "The adopted Visual Studio setup instance was not discovered exactly once.",
            data={"instance_id": instance_id},
        )
    if before.installation_path != ownership.installation_path:
        return OperationResult.failure(
            "visual_studio_instance_identity_mismatch",
            "The adopted instance ID resolves to a different installation path.",
            data={
                "instance": before.to_dict(),
                "owned_installation_path": str(ownership.installation_path),
            },
        )
    if not before.is_complete:
        return OperationResult.failure(
            "visual_studio_instance_incomplete",
            "Refusing to modify an incomplete Visual Studio setup instance.",
            data={"instance": before.to_dict()},
        )

    installed_before = before.component_ids
    to_add = desired - installed_before
    to_remove = ownership.owned_components - desired
    preserved_unowned = installed_before - ownership.owned_components
    data: dict[str, object] = {
        "instance": before.to_dict(),
        "desired_components": sorted(desired),
        "owned_components_before": sorted(ownership.owned_components),
        "add_components": sorted(to_add),
        "remove_components": sorted(to_remove),
        "preserved_unowned_components": sorted(preserved_unowned),
        "restart_required": False,
    }

    if not to_add and not to_remove:
        return OperationResult.success(
            "native_toolchain_components_reconciled",
            "Native toolchain components already satisfy the owned desired state.",
            data=data,
        )

    setup = _setup_path(setup_path=setup_path, environ=environ)
    if setup is None:
        return OperationResult.unsupported(
            "visual_studio_installer_unavailable",
            "Visual Studio Installer setup.exe is not available.",
            data=data,
        )

    argv = [
        setup,
        "modify",
        "--installPath",
        str(before.installation_path),
    ]
    for component in sorted(to_add):
        argv.extend(["--add", component])
    for component in sorted(to_remove):
        argv.extend(["--remove", component])
    argv.extend(["--quiet", "--wait", "--norestart"])
    data["argv"] = argv

    if context.dry_run:
        return OperationResult.success(
            "would_reconcile_native_toolchain_components",
            "Visual Studio components would be reconciled in the adopted instance.",
            data=data,
        )

    mutation = runner(argv)

    try:
        after_instances = discover_visual_studio_instances(
            runner=runner,
            vswhere_path=vswhere_path,
            which=which,
            environ=environ,
            version_lister=version_lister,
        )
    except NativeToolchainDiscoveryError as exc:
        return OperationResult.error(
            "native_toolchain_verification_failed",
            f"Component mutation ran, but rediscovery failed: {exc}",
            changed=True,
            data={
                **data,
                "installer_returncode": mutation.returncode,
                "stderr": mutation.stderr[-2000:],
            },
        )

    after = _find_instance(after_instances, instance_id)
    if after is None or after.installation_path != ownership.installation_path:
        return OperationResult.error(
            "visual_studio_instance_identity_changed",
            "Component mutation ran, but the adopted setup instance identity changed or disappeared.",
            changed=True,
            data={
                **data,
                "installer_returncode": mutation.returncode,
                "stderr": mutation.stderr[-2000:],
            },
        )

    installed_after = after.component_ids
    newly_owned = to_add & installed_after
    still_owned = ownership.owned_components & installed_after
    owned_after = (still_owned | newly_owned) - (to_remove - installed_after)
    updated = ownership.with_owned_components(owned_after)
    _write_ownership(context, updated)

    observed_changed = installed_after != installed_before
    data.update(
        {
            "instance_after": after.to_dict(),
            "owned_components_after": sorted(owned_after),
            "installer_returncode": mutation.returncode,
            "stderr": mutation.stderr[-2000:],
        }
    )

    failure = _installer_result(
        mutation.returncode,
        changed=observed_changed,
        data=data,
    )
    if failure is not None:
        return failure

    missing = desired - installed_after
    owned_removals_still_present = to_remove & installed_after
    if missing or owned_removals_still_present:
        return OperationResult.error(
            "native_toolchain_verification_failed",
            "Visual Studio Installer returned success but component verification did not converge.",
            changed=observed_changed,
            data={
                **data,
                "missing_desired_components": sorted(missing),
                "owned_removals_still_present": sorted(owned_removals_still_present),
            },
        )

    restart_required = mutation.returncode in {
        _SUCCESS_RESTART_REQUIRED,
        _SUCCESS_REBOOT_INITIATED,
    }
    data["restart_required"] = restart_required
    return OperationResult.success(
        "native_toolchain_components_reconciled",
        (
            "Native toolchain components were reconciled; a restart is required."
            if restart_required
            else "Native toolchain components were reconciled."
        ),
        changed=observed_changed,
        data=data,
    )
