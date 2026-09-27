"""Generic operation dispatch by operation/capability, never application ID."""

from __future__ import annotations

from ..discovery import build_operation_context
from ..model import Application, Operation, OperationContext, OperationResult, Support
from .configuration import apply_config, check_config, unapply_config
from .installation import check_installed, install_application, uninstall_application


def perform_operation(
    application: Application,
    operation: Operation,
    context: OperationContext | None = None,
) -> OperationResult:
    """Perform one declared atomic operation through the shared engines."""
    resolved = context or build_operation_context()
    declaration = application.for_platform(resolved.platform)
    if declaration is None:
        return OperationResult.unsupported(
            "platform_unsupported",
            f"{application.display_name} has no declaration for platform {resolved.platform.value}.",
            data={"application": application.id, "platform": resolved.platform.value},
        )

    support = declaration.support_for(operation)
    if support is Support.UNSUPPORTED:
        return OperationResult.unsupported(
            "operation_unsupported",
            f"{operation.value} is unsupported for {application.display_name} on {resolved.platform.value}.",
            data={"application": application.id, "operation": operation.value},
        )
    if support is Support.NOT_IMPLEMENTED:
        return OperationResult.not_implemented(
            "operation_not_implemented",
            f"{operation.value} is declared but not implemented for {application.display_name}.",
            data={"application": application.id, "operation": operation.value},
        )

    if operation is Operation.CHECK_CONFIG:
        return check_config(application, declaration, resolved)
    if operation is Operation.APPLY_CONFIG:
        return apply_config(application, declaration, resolved)
    if operation is Operation.UNAPPLY_CONFIG:
        return unapply_config(application, declaration, resolved)
    if operation is Operation.CHECK_INSTALLED:
        return check_installed(application, declaration, resolved)
    if operation is Operation.INSTALL:
        return install_application(application, declaration, resolved)
    if operation is Operation.UNINSTALL:
        return uninstall_application(application, declaration, resolved)

    raise ValueError(f"Unhandled operation enum: {operation!r}")
