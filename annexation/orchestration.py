"""Composition of atomic application wrappers into multi-operation workflows."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import importlib.util
from pathlib import Path
from typing import Callable, Iterable

from .model import ConflictPolicy, Operation, OperationContext, OperationResult, ResultStatus


class WrapperLoadError(RuntimeError):
    """An atomic wrapper cannot be loaded or violates its contract."""


RunOperation = Callable[[OperationContext | None], OperationResult]
ConfirmReplacement = Callable[["WrapperBinding", OperationResult], bool]


@dataclass(frozen=True)
class WrapperBinding:
    application_id: str
    display_name: str
    operation: Operation
    path: Path
    run: RunOperation


@dataclass(frozen=True)
class OperationAttempt:
    application_id: str
    operation: Operation
    result: OperationResult

    def to_dict(self) -> dict[str, object]:
        return {
            "application": self.application_id,
            "operation": self.operation.value,
            "result": self.result.to_dict(),
        }


@dataclass(frozen=True)
class WorkflowReport:
    attempts: tuple[OperationAttempt, ...]

    @property
    def changed(self) -> bool:
        return any(attempt.result.changed for attempt in self.attempts)

    @property
    def exit_code(self) -> int:
        return max((attempt.result.exit_code for attempt in self.attempts), default=0)

    def to_dict(self) -> dict[str, object]:
        return {
            "changed": self.changed,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }


@dataclass(frozen=True)
class DiscoveryStatusEntry:
    """Three independent read-only discovery dimensions for one application."""

    application_id: str
    display_name: str
    installation: OperationAttempt
    configuration: OperationAttempt
    effective: OperationAttempt

    def to_dict(self) -> dict[str, object]:
        return {
            "application": self.application_id,
            "display_name": self.display_name,
            "installation": self.installation.result.to_dict(),
            "configuration": self.configuration.result.to_dict(),
            "effective": self.effective.result.to_dict(),
        }

    @property
    def attempts(self) -> tuple[OperationAttempt, ...]:
        return (
            self.installation,
            self.configuration,
            self.effective,
        )


@dataclass(frozen=True)
class DiscoveryStatusReport:
    """Grouped status without collapsing dimensions into one health value."""

    applications: tuple[DiscoveryStatusEntry, ...]

    @property
    def exit_code(self) -> int:
        errors = (
            attempt.result.exit_code
            for entry in self.applications
            for attempt in entry.attempts
            if attempt.result.status is ResultStatus.ERROR
        )
        return max(errors, default=0)

    def to_dict(self) -> dict[str, object]:
        return {
            "applications": [entry.to_dict() for entry in self.applications],
        }


def _wrapper_module_name(path: Path) -> str:
    digest = hashlib.sha256(str(path.absolute()).encode("utf-8")).hexdigest()[:16]
    return f"_machine_soul_wrapper_{digest}"


def load_wrapper(path: str | Path) -> WrapperBinding:
    """Load one side-effect-free atomic wrapper and validate its interface."""
    wrapper_path = Path(path).absolute()
    if not wrapper_path.is_file():
        raise WrapperLoadError(f"Atomic wrapper does not exist: {wrapper_path!s}")

    spec = importlib.util.spec_from_file_location(_wrapper_module_name(wrapper_path), wrapper_path)
    if spec is None or spec.loader is None:
        raise WrapperLoadError(f"Unable to create import specification for {wrapper_path!s}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise WrapperLoadError(f"Atomic wrapper raised while importing: {wrapper_path!s}") from exc

    application = getattr(module, "APPLICATION", None)
    operation = getattr(module, "OPERATION", None)
    run = getattr(module, "run", None)

    if application is None or not hasattr(application, "id") or not hasattr(application, "display_name"):
        raise WrapperLoadError(f"{wrapper_path!s} does not expose a valid APPLICATION.")
    if not isinstance(operation, Operation):
        raise WrapperLoadError(f"{wrapper_path!s} does not expose OPERATION as an Operation.")
    if not callable(run):
        raise WrapperLoadError(f"{wrapper_path!s} does not expose callable run(context).")

    return WrapperBinding(
        application_id=application.id,
        display_name=application.display_name,
        operation=operation,
        path=wrapper_path,
        run=run,
    )


def discover_wrappers(repository_root: str | Path) -> tuple[WrapperBinding, ...]:
    """Discover all atomic wrapper interfaces in deterministic order."""
    root = Path(repository_root)
    annexation = root / "annexation"
    if not annexation.is_dir():
        return ()

    bindings: list[WrapperBinding] = []
    seen: set[tuple[str, Operation]] = set()
    for application_dir in sorted((item for item in annexation.iterdir() if item.is_dir()), key=lambda p: p.name):
        for operation in Operation:
            path = application_dir / f"{operation.value}.py"
            if not path.is_file():
                continue
            binding = load_wrapper(path)
            key = (binding.application_id, binding.operation)
            if key in seen:
                raise WrapperLoadError(
                    f"Duplicate wrapper for application={binding.application_id!r}, "
                    f"operation={binding.operation.value!r}."
                )
            seen.add(key)
            bindings.append(binding)

    return tuple(bindings)


def bindings_for_operation(
    bindings: Iterable[WrapperBinding],
    operation: Operation,
    application_ids: Iterable[str] | None = None,
) -> tuple[WrapperBinding, ...]:
    selected = set(application_ids) if application_ids is not None else None
    return tuple(
        binding
        for binding in bindings
        if binding.operation is operation
        and (selected is None or binding.application_id in selected)
    )


def execute_binding(
    binding: WrapperBinding,
    context: OperationContext,
    *,
    confirm_replacement: ConfirmReplacement | None = None,
) -> OperationAttempt:
    """Execute one wrapper, optionally resolving shared replacement confirmation."""
    result = binding.run(context)
    if (
        result.code == "confirmation_required"
        and context.conflict_policy is ConflictPolicy.PROMPT
        and confirm_replacement is not None
    ):
        if confirm_replacement(binding, result):
            result = binding.run(
                replace(context, conflict_policy=ConflictPolicy.BACKUP_AND_REPLACE)
            )
        else:
            result = OperationResult.failure(
                "declined",
                "Operation was declined by the maintainer.",
            )
    return OperationAttempt(binding.application_id, binding.operation, result)


def execute_bindings(
    bindings: Iterable[WrapperBinding],
    context: OperationContext,
    *,
    confirm_replacement: ConfirmReplacement | None = None,
    stop_on_partial_change: bool = True,
) -> WorkflowReport:
    """Execute independent wrappers in order without collapsing their results."""
    attempts: list[OperationAttempt] = []
    for binding in bindings:
        attempt = execute_binding(
            binding,
            context,
            confirm_replacement=confirm_replacement,
        )
        attempts.append(attempt)
        if (
            stop_on_partial_change
            and attempt.result.changed
            and attempt.result.status is not ResultStatus.SUCCESS
        ):
            break
    return WorkflowReport(tuple(attempts))


def check_all_configurations(
    bindings: Iterable[WrapperBinding],
    context: OperationContext,
) -> WorkflowReport:
    """Check configuration state for every discovered application wrapper."""
    return execute_bindings(
        bindings_for_operation(bindings, Operation.CHECK_CONFIG),
        context,
        stop_on_partial_change=False,
    )


def apply_selected_configurations(
    bindings: Iterable[WrapperBinding],
    context: OperationContext,
    application_ids: Iterable[str],
    *,
    confirm_replacement: ConfirmReplacement | None = None,
) -> WorkflowReport:
    """Apply config to an explicit selected set of application IDs."""
    return execute_bindings(
        bindings_for_operation(bindings, Operation.APPLY_CONFIG, application_ids),
        context,
        confirm_replacement=confirm_replacement,
    )


def apply_installed_configurations(
    bindings: Iterable[WrapperBinding],
    context: OperationContext,
    *,
    confirm_replacement: ConfirmReplacement | None = None,
) -> WorkflowReport:
    """Apply config only when check_installed positively detects installation."""
    all_bindings = tuple(bindings)
    checks = {
        binding.application_id: binding
        for binding in bindings_for_operation(all_bindings, Operation.CHECK_INSTALLED)
    }
    applies = {
        binding.application_id: binding
        for binding in bindings_for_operation(all_bindings, Operation.APPLY_CONFIG)
    }

    attempts: list[OperationAttempt] = []
    for application_id in sorted(set(checks) & set(applies)):
        checked = execute_binding(checks[application_id], context)
        attempts.append(checked)
        if checked.result.code not in {"installed_managed", "installed_unmanaged"}:
            continue

        applied = execute_binding(
            applies[application_id],
            context,
            confirm_replacement=confirm_replacement,
        )
        attempts.append(applied)
        if applied.result.changed and applied.result.status is not ResultStatus.SUCCESS:
            break

    return WorkflowReport(tuple(attempts))


_STATUS_OPERATIONS = (
    Operation.CHECK_INSTALLED,
    Operation.CHECK_CONFIG,
    Operation.VERIFY_CONFIG,
)


def discovery_status(
    bindings: Iterable[WrapperBinding],
    context: OperationContext,
) -> DiscoveryStatusReport:
    """Run all three read-only discovery dimensions through atomic wrappers."""
    values = tuple(bindings)
    indexed = {
        (binding.application_id, binding.operation): binding
        for binding in values
        if binding.operation in _STATUS_OPERATIONS
    }
    names = {
        binding.application_id: binding.display_name
        for binding in values
    }

    entries: list[DiscoveryStatusEntry] = []
    for application_id in sorted(names):
        attempts: dict[Operation, OperationAttempt] = {}
        for operation in _STATUS_OPERATIONS:
            binding = indexed.get((application_id, operation))
            if binding is None:
                attempts[operation] = OperationAttempt(
                    application_id,
                    operation,
                    OperationResult.not_implemented(
                        "operation_wrapper_missing",
                        f"Atomic wrapper {operation.value!r} is missing.",
                        data={
                            "application": application_id,
                            "operation": operation.value,
                        },
                    ),
                )
                continue
            attempts[operation] = execute_binding(binding, context)

        entries.append(
            DiscoveryStatusEntry(
                application_id=application_id,
                display_name=names[application_id],
                installation=attempts[Operation.CHECK_INSTALLED],
                configuration=attempts[Operation.CHECK_CONFIG],
                effective=attempts[Operation.VERIFY_CONFIG],
            )
        )

    return DiscoveryStatusReport(tuple(entries))
