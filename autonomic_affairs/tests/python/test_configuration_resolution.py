from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from accumulated_instruments.machine_soul.configuration import (
    ConfigurationResolutionError,
    resolve_configurations,
    resolve_source,
)
from accumulated_instruments.machine_soul.model import (
    Application,
    ConfigurationFile,
    HomeRelativeDestination,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
)


class ConfigurationResolutionTests(unittest.TestCase):
    def _context(self, root: Path, host: str = "fixture_host", account: str = "fixture_user") -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.LINUX,
            host=host,
            target_account=TargetAccount(account, root / "home", True),
        )

    def _app(self) -> tuple[Application, PlatformDeclaration, ConfigurationFile]:
        config = ConfigurationFile(
            name="main",
            source_leaf="config.txt",
            destination=HomeRelativeDestination(".config/example/config.txt"),
        )
        declaration = PlatformDeclaration(platform=Platform.LINUX, capabilities={}, configurations=(config,))
        return Application(id="example", display_name="Example", platforms=(declaration,)), declaration, config

    def test_source_precedence_prefers_host_user_then_host_common(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, _, config = self._app()
            context = self._context(root)
            common = root / "assimilation_directives/example/hosts/fixture_host/common/config.txt"
            user = root / "assimilation_directives/example/hosts/fixture_host/users/fixture_user/config.txt"
            common.parent.mkdir(parents=True)
            common.write_text("common", encoding="utf-8")
            user.parent.mkdir(parents=True)
            user.write_text("user", encoding="utf-8")

            self.assertEqual(user, resolve_source(context, app, config))
            user.unlink()
            self.assertEqual(common, resolve_source(context, app, config))

    def test_default_layers_are_used_after_host_layers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, _, config = self._app()
            context = self._context(root)
            default = root / "assimilation_directives/example/default/common/config.txt"
            default.parent.mkdir(parents=True)
            default.write_text("default", encoding="utf-8")
            self.assertEqual(default, resolve_source(context, app, config))

    def test_resolve_configurations_uses_target_account_home(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, _ = self._app()
            context = self._context(root)
            source = root / "assimilation_directives/example/default/common/config.txt"
            source.parent.mkdir(parents=True)
            source.write_text("x", encoding="utf-8")

            resolved = resolve_configurations(context, app, declaration)
            self.assertEqual(1, len(resolved))
            self.assertEqual(root / "home/.config/example/config.txt", resolved[0].destination)

    def test_missing_source_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, _, config = self._app()
            with self.assertRaises(ConfigurationResolutionError):
                resolve_source(self._context(root), app, config)


if __name__ == "__main__":
    unittest.main()
