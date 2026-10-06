from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from annexation_procedures.configuration_verification import verify_config
from annexation_procedures.model import (
    Application,
    ApplicationConfigProbe,
    CmdAutoRunVerification,
    ConfigurationFile,
    ConfigurationVerificationPlan,
    HomeRelativeDestination,
    LocalAppDataRelativeDestination,
    Operation,
    OperationContext,
    Platform,
    PlatformDeclaration,
    PowerShellProfileDestination,
    ResolvedPathVerification,
    Support,
    TargetAccount,
    WindowsTerminalSettingsDestination,
)
from annexation_procedures.process import ProcessResult


class NativeConfigurationVerificationTests(unittest.TestCase):
    def _context(self, root: Path, platform: Platform) -> OperationContext:
        home = root / "home"
        local = root / "local"
        home.mkdir(parents=True, exist_ok=True)
        local.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["HOME"] = str(home)
        env["PATH"] = "fixture"
        return OperationContext(
            repository_root=root,
            platform=platform,
            host="fixture_host",
            target_account=TargetAccount(
                "fixture_user",
                home,
                True,
                local if platform is Platform.WINDOWS else None,
            ),
            environment=env,
        )

    def test_powershell_uses_declared_host_profile_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.WINDOWS)
            destination = root / "profile/Microsoft.PowerShell_profile.ps1"
            destination.parent.mkdir(parents=True)
            destination.write_text("# fixture\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "profile",
                        "Microsoft.PowerShell_profile.ps1",
                        PowerShellProfileDestination("powershell.exe"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ResolvedPathVerification("profile"),)
                ),
            )
            app = Application(id="powershell", display_name="PowerShell", platforms=(declaration,))

            with patch(
                "annexation_procedures.configuration.shutil.which",
                return_value=r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            ), patch(
                "annexation_procedures.configuration.run_process",
                return_value=ProcessResult(0, str(destination), ""),
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        assessment = result.data["assessment"]
        self.assertEqual("resolution", assessment["strongest_evidence"])
        self.assertEqual(str(destination), assessment["observations"][0]["data"]["destination"])

    def test_windows_terminal_packaged_and_unpacked_paths_are_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.WINDOWS)
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "settings",
                        "settings.json",
                        WindowsTerminalSettingsDestination(),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ResolvedPathVerification("settings", "wt.exe"),)
                ),
            )
            app = Application(
                id="windows_terminal",
                display_name="Windows Terminal",
                platforms=(declaration,),
            )
            packaged = (
                context.target_account.local_app_data
                / "Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState"
            )
            packaged.mkdir(parents=True)
            (packaged / "settings.json").write_text("{}", encoding="utf-8")

            with patch(
                "annexation_procedures.native_configuration_verification.shutil.which",
                return_value=r"C:\Users\fixture\AppData\Local\Microsoft\WindowsApps\wt.exe",
            ):
                packaged_result = verify_config(app, declaration, context)

            self.assertEqual("config_effective", packaged_result.code)
            self.assertIn(
                "Microsoft.WindowsTerminal_8wekyb3d8bbwe",
                packaged_result.data["assessment"]["observations"][0]["data"]["destination"],
            )

            (packaged / "settings.json").unlink()
            packaged.rmdir()
            unpacked = context.target_account.local_app_data / "Microsoft/Windows Terminal"
            unpacked.mkdir(parents=True)
            (unpacked / "settings.json").write_text("{}", encoding="utf-8")

            with patch(
                "annexation_procedures.native_configuration_verification.shutil.which",
                return_value=r"C:\tools\terminal\wt.exe",
            ):
                unpacked_result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", unpacked_result.code)
        self.assertIn(
            "Microsoft/Windows Terminal".replace("/", os.sep),
            unpacked_result.data["assessment"]["observations"][0]["data"]["destination"],
        )

    def test_cmd_autorun_match_is_resolution_effective_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.WINDOWS)
            destination = context.target_account.local_app_data / "MachineSoul/cmd/cmdrc.cmd"
            destination.parent.mkdir(parents=True)
            destination.write_text("@echo off\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "command_file",
                        "cmdrc.cmd",
                        LocalAppDataRelativeDestination("MachineSoul/cmd/cmdrc.cmd"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (CmdAutoRunVerification(),)
                ),
            )
            app = Application(id="cmd", display_name="CMD", platforms=(declaration,))
            expected = f'call "{destination}"'
            original = destination.read_text(encoding="utf-8")

            with patch(
                "annexation_procedures.native_configuration_verification._read_cmd_autorun",
                return_value=expected,
            ):
                result = verify_config(app, declaration, context)
            after = destination.read_text(encoding="utf-8")

        self.assertEqual("config_effective", result.code)
        self.assertEqual("resolution", result.data["assessment"]["strongest_evidence"])
        self.assertEqual(original, after)

    def test_cmd_autorun_mismatch_is_not_effective(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.WINDOWS)
            destination = context.target_account.local_app_data / "MachineSoul/cmd/cmdrc.cmd"
            destination.parent.mkdir(parents=True)
            destination.write_text("@echo off\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "command_file",
                        "cmdrc.cmd",
                        LocalAppDataRelativeDestination("MachineSoul/cmd/cmdrc.cmd"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (CmdAutoRunVerification(),)
                ),
            )

            with patch(
                "annexation_procedures.native_configuration_verification._read_cmd_autorun",
                return_value='call "C:\\other.cmd"',
            ):
                result = verify_config(
                    Application(id="cmd", display_name="CMD", platforms=(declaration,)),
                    declaration,
                    context,
                )

        self.assertEqual("config_not_effective", result.code)

    def test_contour_success_is_application_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.LINUX)
            destination = context.target_account.home / ".config/contour/contour.yml"
            destination.parent.mkdir(parents=True)
            destination.write_text("profiles: {}\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "main",
                        "contour.yml",
                        HomeRelativeDestination(".config/contour/contour.yml"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ApplicationConfigProbe("contour", ("info", "config"), "main"),)
                ),
            )
            app = Application(id="contour", display_name="Contour", platforms=(declaration,))

            with patch(
                "annexation_procedures.native_configuration_verification.shutil.which",
                return_value="/usr/bin/contour",
            ), patch(
                "annexation_procedures.native_configuration_verification.run_process",
                return_value=ProcessResult(0, "configuration inspected\n", ""),
            ):
                result = verify_config(app, declaration, context)

        self.assertEqual("config_effective", result.code)
        self.assertEqual("application", result.data["assessment"]["strongest_evidence"])

    def test_contour_nonzero_probe_is_indeterminate_not_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root, Platform.LINUX)
            destination = context.target_account.home / ".config/contour/contour.yml"
            destination.parent.mkdir(parents=True)
            destination.write_text("profiles: {}\n", encoding="utf-8")
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={Operation.VERIFY_CONFIG: Support.SUPPORTED},
                configurations=(
                    ConfigurationFile(
                        "main",
                        "contour.yml",
                        HomeRelativeDestination(".config/contour/contour.yml"),
                    ),
                ),
                configuration_verification=ConfigurationVerificationPlan(
                    (ApplicationConfigProbe("contour", ("info", "config"), "main"),)
                ),
            )

            with patch(
                "annexation_procedures.native_configuration_verification.shutil.which",
                return_value="/usr/bin/contour",
            ), patch(
                "annexation_procedures.native_configuration_verification.run_process",
                return_value=ProcessResult(64, "", "unsupported command"),
            ):
                result = verify_config(
                    Application(id="contour", display_name="Contour", platforms=(declaration,)),
                    declaration,
                    context,
                )

        self.assertEqual("verification_indeterminate", result.code)
        self.assertEqual("application", result.data["assessment"]["strongest_evidence"])


if __name__ == "__main__":
    unittest.main()
