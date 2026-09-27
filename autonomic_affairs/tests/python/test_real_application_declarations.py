from __future__ import annotations

from pathlib import Path
import unittest

from accumulated_instruments.machine_soul.applications import discover_applications
from accumulated_instruments.machine_soul.model import (
    AptPackage,
    CustomConfiguration,
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
                "oh_my_posh",
                "powershell",
                "windows_terminal",
                "zsh",
            },
            set(self.apps),
        )

    def test_config_capabilities_are_declared_supported_on_present_platforms(self) -> None:
        for app in self.apps.values():
            for declaration in app.platforms:
                self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.APPLY_CONFIG))
                self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.UNAPPLY_CONFIG))
                self.assertEqual(Support.SUPPORTED, declaration.support_for(Operation.CHECK_CONFIG))

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

    def test_unmanaged_install_surfaces_are_explicitly_not_implemented(self) -> None:
        for app in self.apps.values():
            for declaration in app.platforms:
                if (
                    app.id == "fish"
                    and declaration.platform is Platform.LINUX
                ) or (
                    app.id == "oh_my_posh"
                    and declaration.platform is Platform.WINDOWS
                ):
                    continue
                self.assertEqual(Support.NOT_IMPLEMENTED, declaration.support_for(Operation.INSTALL))
                self.assertEqual(Support.NOT_IMPLEMENTED, declaration.support_for(Operation.UNINSTALL))
                self.assertEqual(Support.NOT_IMPLEMENTED, declaration.support_for(Operation.CHECK_INSTALLED))


if __name__ == "__main__":
    unittest.main()
