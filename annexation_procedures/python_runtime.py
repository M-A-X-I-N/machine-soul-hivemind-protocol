"""Windows Python Install Manager runtime backend."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
from typing import Callable

from .model import (
    OperationContext,
    OperationResult,
    Platform,
    RuntimeInstance,
    RuntimeSpec,
)
from .process import ProcessResult, run_process
from .state import read_json_state, write_json_state


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]


class PythonInstallManagerError(RuntimeError):
    """Python Install Manager state could not be addressed safely."""


def _default_which(command: str) -> str | None:
    return shutil.which(command)


def python_manager_runtime_spec(
    manager_id: str,
    *,
    version: str,
    architecture: str | None = None,
    flavor: str | None = None,
    distribution: str = "PythonCore",
) -> RuntimeSpec:
    """Build one exact desired Python-manager runtime specification."""
    if not manager_id.strip():
        raise ValueError("manager_id cannot be empty.")
    return RuntimeSpec(
        subject="python",
        version=version,
        backend="python-install-manager",
        backend_key=manager_id,
        architecture=architecture,
        flavor=flavor,
        distribution=distribution,
        metadata={"manager_id": manager_id},
    )


def _architecture_from_tag(tag: str, raw: dict[str, object]) -> str | None:
    value = raw.get("architecture")
    if isinstance(value, str) and value.strip():
        normalized = value.casefold()
        if normalized in {"amd64", "x86_64", "x64", "64bit"}:
            return "x64"
        if normalized in {"x86", "win32", "32bit"}:
            return "x86"
        if normalized in {"arm64", "aarch64"}:
            return "arm64"
        return value

    lowered = tag.casefold()
    if lowered.endswith("-arm64"):
        return "arm64"
    if lowered.endswith("-32"):
        return "x86"
    if lowered.endswith("-64"):
        return "x64"
    return None


def _flavor_from_tag(tag: str, manager_id: str) -> str | None:
    lowered = tag.casefold()
    identity = manager_id.casefold()
    if "embed" in lowered or "embed" in identity:
        return "embeddable"
    base = re.sub(r"-(?:arm64|32|64)$", "", lowered)
    if re.fullmatch(r"\d+(?:\.\d+)*t", base):
        return "free-threaded"
    return None


class PythonInstallManagerBackend:
    """Concrete per-user runtime backend for the official Windows manager."""

    subject = "python"
    name = "python-install-manager"

    def __init__(
        self,
        *,
        runner: Runner | None = None,
        which: Which = _default_which,
        manager_executable: str | None = None,
    ) -> None:
        self._runner = runner
        self._which = which
        self._manager_executable = manager_executable

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if context.platform is not Platform.WINDOWS:
            raise PythonInstallManagerError(
                "Python Install Manager runtime lifecycle is only supported on Windows."
            )
        if not context.target_account.is_current:
            raise PythonInstallManagerError(
                "Python Install Manager is per-user and cannot safely mutate a non-current target account."
            )

    def _manager(self, context: OperationContext) -> str:
        self._guard_context(context)
        if self._manager_executable:
            return self._manager_executable
        located = self._which("pymanager")
        if not located:
            raise PythonInstallManagerError(
                "The unambiguous 'pymanager' command is not available. "
                "Install/manage the Python Install Manager separately before runtime reconciliation."
            )
        return located

    def _run(self, context: OperationContext, args: list[str]) -> ProcessResult:
        argv = [self._manager(context), *args]
        if self._runner is not None:
            return self._runner(argv)

        environment = dict(os.environ)
        environment.update(context.environment)
        environment.pop("VIRTUAL_ENV", None)
        environment["PYTHON_MANAGER_VIRTUAL_ENV"] = ""
        return run_process(argv, environ=environment)

    def _list_rows(
        self,
        context: OperationContext,
        *,
        only_managed: bool = False,
        default_only: bool = False,
    ) -> list[dict[str, object]]:
        args = ["list", "-q", "--format=json"]
        if only_managed:
            args.append("--only-managed")
        if default_only:
            args.extend(["--one", "default"])
        result = self._run(context, args)
        if result.returncode != 0:
            raise PythonInstallManagerError(
                f"pymanager list failed with exit code {result.returncode}: {result.stderr[-1000:]}"
            )
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise PythonInstallManagerError(
                "pymanager list returned malformed JSON."
            ) from exc
        versions = payload.get("versions", []) if isinstance(payload, dict) else None
        if not isinstance(versions, list):
            raise PythonInstallManagerError(
                "pymanager list JSON must contain a 'versions' array."
            )
        rows: list[dict[str, object]] = []
        for item in versions:
            if not isinstance(item, dict):
                raise PythonInstallManagerError(
                    "pymanager list JSON contains a non-object runtime entry."
                )
            rows.append(item)
        return rows

    def _instance_from_row(
        self,
        raw: dict[str, object],
        *,
        managed_ids: frozenset[str],
    ) -> RuntimeInstance | None:
        manager_id = raw.get("id")
        tag = raw.get("tag")
        company = raw.get("company")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (manager_id, tag, company)
        ):
            raise PythonInstallManagerError(
                "pymanager runtime entry is missing id, tag, or company."
            )
        assert isinstance(manager_id, str)
        assert isinstance(tag, str)
        assert isinstance(company, str)
        if manager_id == "__active-virtual-env":
            return None

        managed = manager_id in managed_ids
        version = str(raw.get("sort-version") or raw.get("version") or tag)
        executable_raw = raw.get("executable")
        prefix_raw = raw.get("prefix")
        display_name = raw.get("display-name")
        selection_tag = f"{company}\\{tag}"

        metadata: dict[str, object] = {
            "manager_id": manager_id,
            "tag": tag,
            "company": company,
            "selection_tag": selection_tag,
            "managed": managed,
        }
        if isinstance(display_name, str):
            metadata["display_name"] = display_name

        return RuntimeInstance(
            subject=self.subject,
            version=version,
            backend=self.name if managed else "python-unmanaged",
            backend_key=manager_id,
            architecture=_architecture_from_tag(tag, raw),
            flavor=_flavor_from_tag(tag, manager_id),
            distribution=company,
            executable=(
                Path(executable_raw)
                if isinstance(executable_raw, str) and executable_raw
                else None
            ),
            prefix=(
                Path(prefix_raw)
                if isinstance(prefix_raw, str) and prefix_raw
                else None
            ),
            metadata=metadata,
        )

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        managed_rows = self._list_rows(context, only_managed=True)
        managed_ids = frozenset(
            str(item["id"])
            for item in managed_rows
            if isinstance(item.get("id"), str)
        )
        all_rows = self._list_rows(context)
        instances = [
            instance
            for item in all_rows
            if (instance := self._instance_from_row(item, managed_ids=managed_ids))
            is not None
        ]
        return tuple(instances)

    def selected_key(self, context: OperationContext) -> str | None:
        # An implicit manager fallback is not durable desired state. Require an
        # explicit native default_tag, then verify that the manager resolves it
        # to one exact managed runtime.
        path = self._user_config_path(context)
        try:
            payload = read_json_state(path) or {}
        except Exception as exc:
            raise PythonInstallManagerError(
                f"Python Install Manager user configuration cannot be read safely: {exc}"
            ) from exc
        default_tag = payload.get("default_tag")
        if not isinstance(default_tag, str) or not default_tag.strip():
            return None

        managed_rows = self._list_rows(context, only_managed=True)
        managed_ids = frozenset(
            str(item["id"])
            for item in managed_rows
            if isinstance(item.get("id"), str)
        )
        rows = self._list_rows(context, default_only=True)
        if not rows:
            return None
        instance = self._instance_from_row(rows[0], managed_ids=managed_ids)
        if instance is None or instance.backend != self.name:
            return None

        selection_tag = instance.metadata.get("selection_tag")
        raw_tag = instance.metadata.get("tag")
        if default_tag not in {selection_tag, raw_tag}:
            return None
        return instance.backend_key

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        if spec.subject != self.subject or spec.backend != self.name:
            return OperationResult.error(
                "python_runtime_spec_mismatch",
                "Python runtime specification does not target this backend.",
                data={"spec": spec.to_dict()},
            )
        args = ["install", "-q", "--yes", "--by-id", spec.backend_key]
        if context.dry_run:
            return OperationResult.success(
                "would_install_python_runtime",
                "Python runtime would be installed by exact manager ID.",
                data={"manager_id": spec.backend_key, "argv": [self._manager(context), *args]},
            )
        result = self._run(context, args)
        if result.returncode != 0:
            return OperationResult.error(
                "python_runtime_install_failed",
                f"pymanager install failed with exit code {result.returncode}.",
                data={"manager_id": spec.backend_key, "stderr": result.stderr[-1000:]},
            )
        return OperationResult.success(
            "python_runtime_installed",
            "Python runtime was installed by exact manager ID.",
            changed=True,
            data={"manager_id": spec.backend_key},
        )

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name:
            return OperationResult.error(
                "python_runtime_instance_mismatch",
                "Refusing to uninstall a runtime not owned by the Python Install Manager backend.",
                data={"instance": instance.to_dict()},
            )
        args = ["uninstall", "-q", "--yes", "--by-id", instance.backend_key]
        if context.dry_run:
            return OperationResult.success(
                "would_uninstall_python_runtime",
                "Python runtime would be uninstalled by exact manager ID.",
                data={"manager_id": instance.backend_key, "argv": [self._manager(context), *args]},
            )
        result = self._run(context, args)
        if result.returncode != 0:
            return OperationResult.error(
                "python_runtime_uninstall_failed",
                f"pymanager uninstall failed with exit code {result.returncode}.",
                data={"manager_id": instance.backend_key, "stderr": result.stderr[-1000:]},
            )
        return OperationResult.success(
            "python_runtime_uninstalled",
            "Python runtime was uninstalled by exact manager ID.",
            changed=True,
            data={"manager_id": instance.backend_key},
        )

    def _user_config_path(self, context: OperationContext) -> Path:
        appdata = context.environment.get("APPDATA")
        if not appdata and context.target_account.is_current:
            appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Python" / "pymanager.json"
        return (
            context.target_account.home
            / "AppData"
            / "Roaming"
            / "Python"
            / "pymanager.json"
        )

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name:
            return OperationResult.error(
                "python_runtime_instance_mismatch",
                "Refusing to select a runtime not managed by this backend.",
                data={"instance": instance.to_dict()},
            )
        selection_tag = instance.metadata.get("selection_tag")
        if not isinstance(selection_tag, str) or not selection_tag.strip():
            return OperationResult.error(
                "python_runtime_selection_tag_missing",
                "Managed Python runtime discovery did not expose a selection tag.",
                data={"instance": instance.to_dict()},
            )

        path = self._user_config_path(context)
        try:
            payload = read_json_state(path) or {}
        except Exception as exc:
            return OperationResult.error(
                "python_manager_config_invalid",
                f"Python Install Manager user configuration cannot be read safely: {exc}",
                data={"path": str(path)},
            )

        if payload.get("default_tag") == selection_tag:
            return OperationResult.success(
                "python_runtime_selected",
                "Python Install Manager default already selects the desired runtime.",
                data={"default_tag": selection_tag, "path": str(path)},
            )
        if context.dry_run:
            return OperationResult.success(
                "would_select_python_runtime",
                "Python Install Manager default_tag would be updated.",
                data={"default_tag": selection_tag, "path": str(path)},
            )

        payload["default_tag"] = selection_tag
        try:
            write_json_state(path, payload)
        except Exception as exc:
            return OperationResult.error(
                "python_manager_config_write_failed",
                f"Python Install Manager user configuration could not be updated: {exc}",
                data={"path": str(path), "default_tag": selection_tag},
            )
        return OperationResult.success(
            "python_runtime_selected",
            "Python Install Manager default_tag was updated.",
            changed=True,
            data={"default_tag": selection_tag, "path": str(path)},
        )
