"""Generic Machine-Soul operation dispatcher and engines."""

from .configuration import apply_config, check_config, unapply_config
from .dispatcher import perform_operation
from .installation import check_installed, install_application, uninstall_application

__all__ = [
    "perform_operation",
    "apply_config",
    "check_config",
    "unapply_config",
    "check_installed",
    "install_application",
    "uninstall_application",
]
