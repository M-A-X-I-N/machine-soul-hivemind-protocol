from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from annexation_procedures.applications import load_application
from annexation_procedures.model import Operation
from annexation_procedures.operations import perform_operation
from annexation_procedures.presentation import wrapper_main


APPLICATION = load_application(Path(__file__).with_name("_application.py"))
OPERATION = Operation.CHECK_INSTALLED


def run(context=None):
    return perform_operation(APPLICATION, OPERATION, context)


def main(argv=None):
    return wrapper_main(run, argv)


if __name__ == "__main__":
    raise SystemExit(main())
