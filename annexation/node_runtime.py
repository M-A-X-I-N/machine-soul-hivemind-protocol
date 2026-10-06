"""Windows nvm-windows v2 Node.js runtime backend."""

from __future__ import annotations

import json
import ntpath
from pathlib import Path
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


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]


class NvmWindowsV2Error(RuntimeError):
    """nvm-windows v2 state could not be addressed safely."""


def _default_which(command: str) -> str | None:
    return shutil.which(command)


def nvm_windows_runtime_spec(
    version: str,
    *,
    architecture: str | None = None,
) -> RuntimeSpec:
    """Build one exact desired nvm-windows Node runtime specification."""
    exact = version.strip().removeprefix("v")
    if not exact:
        raise ValueError("Node version cannot be empty.")
    return RuntimeSpec(
        subject="node",
        version=exact,
        backend="nvm-windows-v2",
        backend_key=exact,
        architecture=architecture,
        distribution="nodejs",
    )


def _normalized_architecture(value: str) -> str:
    normalized = value.strip().casefold()
    if normalized in {"x64", "amd64", "x86_64"}:
        return "x64"
    if normalized in {"ia32", "x86", "win32"}:
        return "x86"
    if normalized in {"arm64", "aarch64"}:
        return "arm64"
    return value.strip()


class NvmWindowsV2Backend:
    """Concrete current-user runtime backend for nvm-windows v2."""

    subject = "node"
    name = "nvm-windows-v2"

    def __init__(
        self,
        *,
        runner: Runner = run_process,
        which: Which = _default_which,
        nvm_executable: str | None = None,
    ) -> None:
        self._runner = runner
        self._which = which
        self._nvm_executable = nvm_executable

    def ownership_scope(self, context: OperationContext) -> str | None:
        self._guard_context(context)
        return f"user:{context.target_account.name.casefold()}"

    def _guard_context(self, context: OperationContext) -> None:
        if context.platform is not Platform.WINDOWS:
            raise NvmWindowsV2Error(
                "nvm-windows v2 runtime lifecycle is only supported on Windows."
            )
        if not context.target_account.is_current:
            raise NvmWindowsV2Error(
                "nvm-windows v2 is per-user and cannot safely mutate a non-current target account."
            )

    def _nvm(self, context: OperationContext) -> str:
        self._guard_context(context)
        if self._nvm_executable:
            return self._nvm_executable
        located = self._which("nvm")
        if not located:
            raise NvmWindowsV2Error(
                "nvm-windows is not available. Manage the version manager separately "
                "before reconciling Node runtimes."
            )
        return located

    def _run(self, context: OperationContext, args: list[str]) -> ProcessResult:
        return self._runner([self._nvm(context), *args])

    def _json_command(
        self,
        context: OperationContext,
        args: list[str],
        *,
        expected: type,
    ):
        result = self._run(context, args)
        if result.returncode != 0:
            raise NvmWindowsV2Error(
                f"nvm {' '.join(args)} failed with exit code {result.returncode}: "
                f"{result.stderr[-1000:]}"
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise NvmWindowsV2Error(
                f"nvm {' '.join(args)} returned malformed JSON."
            ) from exc
        if not isinstance(payload, expected):
            raise NvmWindowsV2Error(
                f"nvm {' '.join(args)} returned unexpected JSON shape."
            )
        return payload

    def _environment(self, context: OperationContext) -> dict[str, object]:
        payload = self._json_command(
            context,
            ["config", "get", "root", "mode", "--json"],
            expected=dict,
        )
        root = payload.get("root")
        mode = payload.get("mode")
        if not isinstance(root, str) or not root.strip():
            raise NvmWindowsV2Error(
                "nvm config get root mode --json is missing root."
            )
        manager_executable = self._nvm(context)
        return {
            "version_root": root,
            "mode": mode if isinstance(mode, str) else None,
            "program_root": ntpath.dirname(manager_executable),
            "manager_executable": manager_executable,
        }

    def _installed_rows(
        self,
        context: OperationContext,
    ) -> list[dict[str, object]]:
        payload = self._json_command(context, ["list", "--json"], expected=list)
        rows: list[dict[str, object]] = []
        for item in payload:
            if not isinstance(item, dict):
                raise NvmWindowsV2Error(
                    "nvm list --json contains a non-object version entry."
                )
            if item.get("installed") is False:
                continue
            version = item.get("version")
            if not isinstance(version, str) or not version.strip():
                raise NvmWindowsV2Error(
                    "nvm list --json contains an installed entry without a version."
                )
            rows.append(item)
        return rows

    def _probe_node(
        self,
        executable: str,
    ) -> tuple[str, str]:
        version_result = self._runner([executable, "--version"])
        if version_result.returncode != 0:
            raise NvmWindowsV2Error(
                f"Node runtime probe failed for {executable!r}: "
                f"{version_result.stderr[-1000:]}"
            )
        version = version_result.stdout.strip().removeprefix("v")
        if not version:
            raise NvmWindowsV2Error(
                f"Node runtime probe returned no version for {executable!r}."
            )

        arch_result = self._runner([executable, "-p", "process.arch"])
        if arch_result.returncode != 0:
            raise NvmWindowsV2Error(
                f"Node architecture probe failed for {executable!r}: "
                f"{arch_result.stderr[-1000:]}"
            )
        architecture = _normalized_architecture(arch_result.stdout)
        if not architecture:
            raise NvmWindowsV2Error(
                f"Node architecture probe returned no value for {executable!r}."
            )
        return version, architecture

    def _managed_instances(
        self,
        context: OperationContext,
        environment: dict[str, object],
    ) -> tuple[RuntimeInstance, ...]:
        root = str(environment["version_root"])
        mode = environment.get("mode")
        manager_executable = environment.get("manager_executable")

        instances: list[RuntimeInstance] = []
        for row in self._installed_rows(context):
            listed_version = str(row["version"]).removeprefix("v")
            prefix_raw = ntpath.join(root, f"v{listed_version}")
            executable_raw = ntpath.join(prefix_raw, "node.exe")
            probed_version, architecture = self._probe_node(executable_raw)
            if probed_version != listed_version:
                raise NvmWindowsV2Error(
                    "nvm inventory and direct Node runtime probe disagree for "
                    f"{listed_version!r}: observed {probed_version!r}."
                )

            metadata: dict[str, object] = {
                "nvm_root": root,
                "nvm_mode": mode,
                "manager_executable": manager_executable,
                "bundled_npm_version": row.get("npm"),
                "nvm_default": bool(row.get("default", False)),
            }
            instances.append(
                RuntimeInstance(
                    subject=self.subject,
                    version=listed_version,
                    backend=self.name,
                    backend_key=listed_version,
                    architecture=architecture,
                    distribution="nodejs",
                    executable=Path(executable_raw),
                    prefix=Path(prefix_raw),
                    metadata=metadata,
                )
            )
        return tuple(instances)

    def _unmanaged_path_candidate(
        self,
        environment: dict[str, object],
        managed: tuple[RuntimeInstance, ...],
    ) -> RuntimeInstance | None:
        node_path = self._which("node")
        if not node_path:
            return None

        normalized = ntpath.normcase(ntpath.normpath(node_path))
        managed_paths = {
            ntpath.normcase(ntpath.normpath(str(item.executable)))
            for item in managed
            if item.executable is not None
        }
        if normalized in managed_paths:
            return None

        program_root = environment.get("program_root")
        if isinstance(program_root, str) and program_root.strip():
            manager_root = ntpath.normcase(ntpath.normpath(program_root))
            if normalized == manager_root or normalized.startswith(manager_root + "\\"):
                return None

        version, architecture = self._probe_node(node_path)
        return RuntimeInstance(
            subject=self.subject,
            version=version,
            backend="node-unmanaged",
            backend_key=f"path:{normalized}",
            architecture=architecture,
            distribution="nodejs",
            executable=Path(node_path),
            prefix=Path(ntpath.dirname(node_path)),
            metadata={"path_candidate": True},
        )

    def discover(self, context: OperationContext) -> tuple[RuntimeInstance, ...]:
        environment = self._environment(context)
        managed = self._managed_instances(context, environment)
        unmanaged = self._unmanaged_path_candidate(environment, managed)
        return managed + ((unmanaged,) if unmanaged is not None else ())

    def selected_key(self, context: OperationContext) -> str | None:
        payload = self._json_command(context, ["default", "--json"], expected=dict)
        selected = payload.get("default")
        if not isinstance(selected, str):
            raise NvmWindowsV2Error("nvm default --json is missing default.")
        normalized = selected.strip().removeprefix("v")
        if not normalized or normalized.casefold() == "none":
            return None
        return normalized

    def install(self, context: OperationContext, spec: RuntimeSpec) -> OperationResult:
        if spec.subject != self.subject or spec.backend != self.name:
            return OperationResult.error(
                "node_runtime_spec_mismatch",
                "Node runtime specification does not target nvm-windows v2.",
                data={"spec": spec.to_dict()},
            )
        args = ["install", spec.backend_key, "--no-cache"]
        if context.dry_run:
            return OperationResult.success(
                "would_install_node_runtime",
                "Node runtime would be installed through nvm-windows v2.",
                data={"version": spec.backend_key, "argv": [self._nvm(context), *args]},
            )
        result = self._run(context, args)
        if result.returncode != 0:
            return OperationResult.error(
                "node_runtime_install_failed",
                f"nvm install failed with exit code {result.returncode}.",
                data={"version": spec.backend_key, "stderr": result.stderr[-1000:]},
            )
        return OperationResult.success(
            "node_runtime_installed",
            "Node runtime was installed through nvm-windows v2.",
            changed=True,
            data={"version": spec.backend_key},
        )

    def uninstall(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name:
            return OperationResult.error(
                "node_runtime_instance_mismatch",
                "Refusing to uninstall a runtime not owned by nvm-windows v2.",
                data={"instance": instance.to_dict()},
            )
        args = ["uninstall", instance.backend_key]
        if context.dry_run:
            return OperationResult.success(
                "would_uninstall_node_runtime",
                "Node runtime would be uninstalled through nvm-windows v2.",
                data={"version": instance.backend_key, "argv": [self._nvm(context), *args]},
            )
        result = self._run(context, args)
        if result.returncode != 0:
            return OperationResult.error(
                "node_runtime_uninstall_failed",
                f"nvm uninstall failed with exit code {result.returncode}.",
                data={"version": instance.backend_key, "stderr": result.stderr[-1000:]},
            )
        return OperationResult.success(
            "node_runtime_uninstalled",
            "Node runtime was uninstalled through nvm-windows v2.",
            changed=True,
            data={"version": instance.backend_key},
        )

    def select(
        self,
        context: OperationContext,
        instance: RuntimeInstance,
    ) -> OperationResult:
        if instance.backend != self.name:
            return OperationResult.error(
                "node_runtime_instance_mismatch",
                "Refusing to select a runtime not owned by nvm-windows v2.",
                data={"instance": instance.to_dict()},
            )
        # --no-install makes selection incapable of silently expanding the
        # desired installed set through nvm's optional auto-install behavior.
        args = ["use", instance.backend_key, "--no-install"]
        if context.dry_run:
            return OperationResult.success(
                "would_select_node_runtime",
                "nvm-windows default Node runtime would be changed.",
                data={"version": instance.backend_key, "argv": [self._nvm(context), *args]},
            )
        result = self._run(context, args)
        if result.returncode != 0:
            return OperationResult.error(
                "node_runtime_selection_failed",
                f"nvm use failed with exit code {result.returncode}.",
                data={"version": instance.backend_key, "stderr": result.stderr[-1000:]},
            )
        return OperationResult.success(
            "node_runtime_selected",
            "nvm-windows default Node runtime was changed.",
            changed=True,
            data={"version": instance.backend_key},
        )
