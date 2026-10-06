from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from annexation_procedures.configuration import resolve_destination
from annexation_procedures.model import (
    ConfigurationFile,
    LocalAppDataRelativeDestination,
    OperationContext,
    Platform,
    PowerShellProfileDestination,
    TargetAccount,
    WindowsPosixHomeDestination,
    WindowsTerminalSettingsDestination,
)
from annexation_procedures.process import ProcessResult


class DestinationStrategyTests(unittest.TestCase):
    def _context(
        self,
        root: Path,
        *,
        local_app_data: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture_host",
            target_account=TargetAccount(
                "fixture_user",
                root / "home",
                True,
                local_app_data=local_app_data,
            ),
            environment=environment or {},
        )

    def _config(self, strategy: object) -> ConfigurationFile:
        return ConfigurationFile(name="main", source_leaf="config.txt", destination=strategy)

    def test_local_app_data_relative_destination(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, local_app_data=root / "local")
            result = resolve_destination(
                context,
                self._config(LocalAppDataRelativeDestination("vendor/config.txt")),
            )
            self.assertEqual(root / "local/vendor/config.txt", result)

    def test_windows_terminal_prefers_packaged_directory_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            local = root / "local"
            packaged = (
                local
                / "Packages"
                / "Microsoft.WindowsTerminal_8wekyb3d8bbwe"
                / "LocalState"
            )
            packaged.mkdir(parents=True)
            context = self._context(root, local_app_data=local)
            result = resolve_destination(
                context,
                self._config(WindowsTerminalSettingsDestination()),
            )
            self.assertEqual(packaged / "settings.json", result)

    def test_powershell_profile_uses_shared_process_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, environment={"PATH": "fixture"})
            expected = root / "profile.ps1"
            with patch(
                "annexation_procedures.configuration.shutil.which",
                return_value="powershell.exe",
            ), patch(
                "annexation_procedures.configuration.run_process",
                return_value=ProcessResult(0, str(expected), ""),
            ):
                result = resolve_destination(
                    context,
                    self._config(PowerShellProfileDestination()),
                )
            self.assertEqual(expected, result)

    def test_windows_posix_home_uses_cygpath_without_mangling_posix_home(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(
                root,
                environment={"HOME": "/c/Users/fixture", "PATH": "fixture"},
            )
            with patch(
                "annexation_procedures.configuration.shutil.which",
                return_value="cygpath",
            ), patch(
                "annexation_procedures.configuration.run_process",
                return_value=ProcessResult(0, r"C:\Users\fixture\.config\fish\config.fish", ""),
            ) as runner:
                result = resolve_destination(
                    context,
                    self._config(
                        WindowsPosixHomeDestination(".config/fish/config.fish")
                    ),
                )
            self.assertEqual(
                Path(r"C:\Users\fixture\.config\fish\config.fish"),
                result,
            )
            self.assertEqual(
                "/c/Users/fixture/.config/fish/config.fish",
                runner.call_args.args[0][2],
            )

    def test_environment_is_copied_into_operation_context(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            source = {"HOME": "/fixture"}
            context = self._context(Path(raw), environment=source)
            source["HOME"] = "/changed"
            self.assertEqual("/fixture", context.environment["HOME"])
            with self.assertRaises(TypeError):
                context.environment["HOME"] = "/nope"  # type: ignore[index]


if __name__ == "__main__":
    unittest.main()
