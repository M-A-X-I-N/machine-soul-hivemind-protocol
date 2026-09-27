from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from accumulated_instruments.machine_soul.model import (
    Application,
    CustomConfiguration,
    Operation,
    OperationContext,
    OperationResult,
    Platform,
    PlatformDeclaration,
    Support,
    TargetAccount,
)
from accumulated_instruments.machine_soul.operations import perform_operation


class CustomConfigurationDispatcherTests(unittest.TestCase):
    def test_dispatcher_calls_declared_custom_configuration_hook(self) -> None:
        calls = []

        def handler(application, declaration, operation, context):
            calls.append((application.id, operation, context.host))
            return OperationResult.success("custom_done", "Custom config hook ran.")

        declaration = PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={Operation.CHECK_CONFIG: Support.SUPPORTED},
            configuration_strategy=CustomConfiguration(handler),
        )
        app = Application(id="example", display_name="Example", platforms=(declaration,))
        with tempfile.TemporaryDirectory() as raw:
            context = OperationContext(
                repository_root=Path(raw),
                platform=Platform.WINDOWS,
                host="fixture_host",
                target_account=TargetAccount("fixture_user", Path(raw) / "home", True),
            )
            result = perform_operation(app, Operation.CHECK_CONFIG, context)

        self.assertEqual("custom_done", result.code)
        self.assertEqual([("example", Operation.CHECK_CONFIG, "fixture_host")], calls)


if __name__ == "__main__":
    unittest.main()
