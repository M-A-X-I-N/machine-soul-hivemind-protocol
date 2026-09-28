from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    AptPackage,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    HomeRelativeDestination,
    ShellStartupVerification,
    WindowsPosixHomeDestination,
    WindowsPosixPackageDiscovery,
)

APPLICATION = Application(
    id="fish",
    display_name="Fish",
    platforms=(
        PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.VERIFY_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.SUPPORTED,
            Operation.UNINSTALL: Support.SUPPORTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
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
                (
                    DpkgPackageDiscovery(
                        "fish",
                        executable_name="fish",
                        preferred=True,
                    ),
                    ExecutableDiscovery("fish", ("--version",)),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ShellStartupVerification("fish", "fish", "main"),)
            ),
        ),
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.VERIFY_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf="config.fish",
                    destination=WindowsPosixHomeDestination(".config/fish/config.fish"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WindowsPosixPackageDiscovery(
                        "fish",
                        "fish",
                        ("--version",),
                    ),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ShellStartupVerification("fish", "fish", "main"),)
            ),
        ),
    ),
)
