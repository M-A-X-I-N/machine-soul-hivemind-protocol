from __future__ import annotations

import unittest

from annexation_procedures.model import (
    Application,
    AptPackage,
    DpkgPackageDiscovery,
    InstallationDiscoveryPlan,
    ConfigurationFile,
    HomeRelativeDestination,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
)


class ApplicationModelTests(unittest.TestCase):
    def test_side_effect_free_declaration_shape(self) -> None:
        fish = Application(
            id="fish",
            display_name="Fish",
            platforms=(
                PlatformDeclaration(
                    platform=Platform.LINUX,
                    capabilities={
                        Operation.APPLY_CONFIG: Support.SUPPORTED,
                        Operation.CHECK_CONFIG: Support.SUPPORTED,
                        Operation.INSTALL: Support.SUPPORTED,
                    },
                    configurations=(
                        ConfigurationFile(
                            name="main",
                            source_leaf="config.fish",
                            destination=HomeRelativeDestination(".config/fish/config.fish"),
                        ),
                    ),
                    install_strategy=AptPackage("fish"),
                    installation_discovery=InstallationDiscoveryPlan(
                        (DpkgPackageDiscovery("fish", preferred=True),)
                    ),
                ),
            ),
        )

        linux = fish.for_platform(Platform.LINUX)
        self.assertIsNotNone(linux)
        assert linux is not None
        self.assertEqual(Support.SUPPORTED, linux.support_for(Operation.INSTALL))
        self.assertEqual(Support.UNSUPPORTED, linux.support_for(Operation.UNINSTALL))

    def test_repository_owned_application_id_must_be_snake_case(self) -> None:
        with self.assertRaises(ValueError):
            Application(id="oh-my-posh", display_name="Oh My Posh", platforms=())

    def test_supported_install_requires_strategy(self) -> None:
        with self.assertRaises(ValueError):
            PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={Operation.INSTALL: Support.SUPPORTED},
            )

    def test_supported_check_installed_requires_discovery_plan(self) -> None:
        with self.assertRaises(ValueError):
            PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={Operation.CHECK_INSTALLED: Support.SUPPORTED},
            )

    def test_discovery_plan_does_not_require_install_strategy(self) -> None:
        declaration = PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={Operation.CHECK_INSTALLED: Support.SUPPORTED},
            installation_discovery=InstallationDiscoveryPlan(
                (DpkgPackageDiscovery("example"),)
            ),
        )
        self.assertIsNone(declaration.install_strategy)
        self.assertIsNotNone(declaration.installation_discovery)

    def test_duplicate_platform_declaration_is_rejected(self) -> None:
        linux = PlatformDeclaration(platform=Platform.LINUX, capabilities={})
        with self.assertRaises(ValueError):
            Application(
                id="fish",
                display_name="Fish",
                platforms=(linux, linux),
            )

    def test_source_leaf_cannot_hide_path_resolution(self) -> None:
        with self.assertRaises(ValueError):
            ConfigurationFile(
                name="main",
                source_leaf="host/config.fish",
                destination=HomeRelativeDestination(".config/fish/config.fish"),
            )


if __name__ == "__main__":
    unittest.main()
