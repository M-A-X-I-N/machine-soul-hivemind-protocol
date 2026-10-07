from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation.model import (
    Application,
    ConfigurationFile,
    ConflictPolicy,
    HomeRelativeDestination,
    Operation,
    OperationContext,
    Platform,
    PlatformDeclaration,
    Support,
    TargetAccount,
)
from annexation.operations import perform_operation


class DispatcherTests(unittest.TestCase):
    def test_dispatches_supported_config_operations_and_capability_states(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".machine_soul_root").write_text("marker\n", encoding="utf-8")
            source = root / "assimilation/example/default/common/config.txt"
            source.parent.mkdir(parents=True)
            source.write_text("canonical", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={
                    Operation.CHECK_CONFIG: Support.SUPPORTED,
                    Operation.APPLY_CONFIG: Support.SUPPORTED,
                    Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
                    Operation.INSTALL: Support.UNSUPPORTED,
                    Operation.CHECK_INSTALLED: Support.NOT_IMPLEMENTED,
                },
                configurations=(
                    ConfigurationFile(
                        name="main",
                        source_leaf="config.txt",
                        destination=HomeRelativeDestination(".config/example/config.txt"),
                    ),
                ),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = OperationContext(
                repository_root=root,
                platform=Platform.LINUX,
                host="fixture_host",
                target_account=TargetAccount("fixture_user", root / "home", True),
                conflict_policy=ConflictPolicy.BACKUP_AND_REPLACE,
            )

            self.assertEqual("not_applied", perform_operation(app, Operation.CHECK_CONFIG, context).code)
            self.assertEqual("applied", perform_operation(app, Operation.APPLY_CONFIG, context).code)
            self.assertEqual("operation_unsupported", perform_operation(app, Operation.INSTALL, context).code)
            self.assertEqual(
                "operation_not_implemented",
                perform_operation(app, Operation.CHECK_INSTALLED, context).code,
            )
            self.assertEqual("not_applied", perform_operation(app, Operation.UNAPPLY_CONFIG, context).code)

    def test_missing_platform_declaration_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app = Application(id="example", display_name="Example", platforms=())
            context = OperationContext(
                repository_root=root,
                platform=Platform.LINUX,
                host="fixture_host",
                target_account=TargetAccount("fixture_user", root / "home", True),
            )
            self.assertEqual(
                "platform_unsupported",
                perform_operation(app, Operation.CHECK_CONFIG, context).code,
            )


if __name__ == "__main__":
    unittest.main()
