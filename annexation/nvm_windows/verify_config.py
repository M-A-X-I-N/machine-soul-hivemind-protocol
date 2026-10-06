from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from annexation.applications import load_application
from annexation.model import Operation
from annexation.operations import perform_operation
from annexation.presentation import wrapper_main


APPLICATION = load_application(Path(__file__).with_name("_application.py"))
_OPERATION_BY_STEM = {
    "apply_config": Operation.APPLY_CONFIG,
    "unapply_config": Operation.UNAPPLY_CONFIG,
    "check_config": Operation.CHECK_CONFIG,
    "verify_config": Operation.VERIFY_CONFIG,
    "install": Operation.INSTALL,
    "uninstall": Operation.UNINSTALL,
    "check_installed": Operation.CHECK_INSTALLED,
}
OPERATION = _OPERATION_BY_STEM[Path(__file__).stem]


def run(context=None):
    return perform_operation(APPLICATION, OPERATION, context)


def main(argv=None):
    return wrapper_main(run, argv)


if __name__ == "__main__":
    raise SystemExit(main())
