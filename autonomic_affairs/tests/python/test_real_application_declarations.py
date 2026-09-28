from __future__ import annotations

from pathlib import Path
import unittest

from annexation_procedures.applications import discover_applications
from annexation_procedures.model import (
    AptPackage,
    CustomConfiguration,
    InstallationScope,
    LocalAppDataRelativeDestination,
    Operation,
    Platform,
    PowerShellProfileDestination,
    Support,
    WindowsPosixHomeDestination,
    WindowsTerminalSettingsDestination,
    WingetPackage,
)


class RealApplicationDeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[3]
        cls.apps = {app.id: app for app in discover_applications(cls.root)}

    def test_expected_application_set_is_discoverable(self) -> None:
        self.assertEqual(
            {
                "bash",
                "cmd",
                "contour",
                "fish",
                "jetbrains_toolbox",
                "oh_my_posh",
                "powershell",
                "python_install_manager",
                "visual_studio_code",
                "windows_terminal",
                "zsh",
            },
            set(self.apps),
        )

    def test_config_capabilities_are_declared_supported_on_present_platforms(self) -> None:
        install_only = {"jetbrains_toolbox", "python_install_manager", "visual_studio_code"}
        for app in self.apps.values():
            for declaration in app.platforms:
                expected = Support.UNSUPPORTED if app.id in install_only else Support.SUPPORTED
                self.assertEqual(expected, declaration.support_for(Operation.APPLY_CONFIG))
                self.assertEqual(expected, declaration.support_for(Operation.UNAPPLY_CONFIG))
                self.assertEqual(expected, declaration.support_for(Operation.CHECK_CONFIG))

    def test_install_strategies_match_current_managed_examples(self) -> None:
        fish_linux = self.apps["fish"].for_platform(Platform.LINUX)
        assert fish_linux is not None
        self.assertIsInstance(fish_linux.install_strategy, AptPackage)
        self.assertEqual(Support.SUPPORTED, fish_linux.support_for(Operation.INSTALL))
        self.assertEqual(Support.SUPPORTED, fish_linux.support_for(Operation.UNINSTALL))
        self.assertEqual(Support.SUPPORTED, fish_linux.support_for(Operation.CHECK_INSTALLED))

        omp_windows = self.apps["oh_my_posh"].for_platform(Platform.WINDOWS)
        assert omp_windows is not None
        self.assertIsInstance(omp_windows.install_strategy, WingetPackage)
        assert isinstance(omp_windows.install_strategy, WingetPackage)
        self.assertEqual("JanDeDobbeleer.OhMyPosh", omp_windows.install_strategy.package_id)

        for app_id, package_id in (
            ("visual_studio_code", "Microsoft.VisualStudioCode"),
            ("jetbrains_toolbox", "JetBrains.Toolbox"),
            ("python_install_manager", "9NQ7512CXL7T"),
        ):
            declaration = self.apps[app_id].for_platform(Platform.WINDOWS)
            assert declaration is not None
            self.assertIsInstance(declaration.install_strategy, WingetPackage)
            assert isinstance(declaration.install_strategy, WingetPackage)
            self.assertEqual(package_id, declaration.install_strategy.package_id)
            self.assertEqual(InstallationScope.USER, declaration.install_strategy.scope_policy.scope)
            self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.INSTALL))
            self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.UNINSTALL))
            self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.CHECK_INSTALLED))

    def test_native_windows_discovery_is_supported_independently_from_install(self) -> None:
        expected = {
            "cmd",
            "contour",
            "jetbrains_toolbox",
            "oh_my_posh",
            "powershell",
            "python_install_manager",
            "visual_studio_code",
            "windows_terminal",
        }
        supported = set()
        for app_id in expected:
            declaration = self.apps[app_id].for_platform(Platform.WINDOWS)
            assert declaration is not None
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.CHECK_INSTALLED),
            )
            self.assertIsNotNone(declaration.installation_discovery)
            supported.add(app_id)

        self.assertEqual(expected, supported)

    def test_native_verification_capabilities_are_wired(self) -> None:
        expected = {
            ("cmd", Platform.WINDOWS),
            ("powershell", Platform.WINDOWS),
            ("windows_terminal", Platform.WINDOWS),
            ("contour", Platform.LINUX),
            ("contour", Platform.WINDOWS),
        }
        for app_id, platform in expected:
            declaration = self.apps[app_id].for_platform(platform)
            assert declaration is not None
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.VERIFY_CONFIG),
            )
            self.assertIsNotNone(declaration.configuration_verification)

    def test_windows_destination_strategies_are_declarative(self) -> None:
        for app_id in ("bash", "fish", "zsh"):
            declaration = self.apps[app_id].for_platform(Platform.WINDOWS)
            assert declaration is not None
            self.assertIsInstance(
                declaration.configurations[0].destination,
                WindowsPosixHomeDestination,
            )

        contour = self.apps["contour"].for_platform(Platform.WINDOWS)
        omp = self.apps["oh_my_posh"].for_platform(Platform.WINDOWS)
        powershell = self.apps["powershell"].for_platform(Platform.WINDOWS)
        terminal = self.apps["windows_terminal"].for_platform(Platform.WINDOWS)
        assert contour and omp and powershell and terminal
        self.assertIsInstance(contour.configurations[0].destination, LocalAppDataRelativeDestination)
        self.assertIsInstance(omp.configurations[0].destination, LocalAppDataRelativeDestination)
        self.assertIsInstance(powershell.configurations[0].destination, PowerShellProfileDestination)
        self.assertIsInstance(terminal.configurations[0].destination, WindowsTerminalSettingsDestination)

    def test_cmd_is_the_only_custom_configuration_strategy(self) -> None:
        custom = []
        for app in self.apps.values():
            for declaration in app.platforms:
                if isinstance(declaration.configuration_strategy, CustomConfiguration):
                    custom.append((app.id, declaration.platform))
        self.assertEqual([("cmd", Platform.WINDOWS)], custom)

    def test_unmanaged_install_mutations_are_explicitly_not_implemented(self) -> None:
        for app in self.apps.values():
            for declaration in app.platforms:
                managed = {
                    ("fish", Platform.LINUX),
                    ("oh_my_posh", Platform.WINDOWS),
                    ("visual_studio_code", Platform.WINDOWS),
                    ("jetbrains_toolbox", Platform.WINDOWS),
                    ("python_install_manager", Platform.WINDOWS),
                }
                if (app.id, declaration.platform) in managed:
                    continue
                self.assertEqual(Support.NOT_IMPLEMENTED, declaration.support_for(Operation.INSTALL))
                self.assertEqual(Support.NOT_IMPLEMENTED, declaration.support_for(Operation.UNINSTALL))

    def test_linux_discovery_is_supported_without_requiring_install_mutation(self) -> None:
        expected = {"bash", "contour", "fish", "oh_my_posh", "zsh"}
        supported = set()
        for app_id in expected:
            declaration = self.apps[app_id].for_platform(Platform.LINUX)
            assert declaration is not None
            self.assertEqual(
                Support.SUPPORTED,
                declaration.support_for(Operation.CHECK_INSTALLED),
            )
            self.assertIsNotNone(declaration.installation_discovery)
            supported.add(app_id)

        self.assertEqual(expected, supported)


if __name__ == "__main__":
    unittest.main()
