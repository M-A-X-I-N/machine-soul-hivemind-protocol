from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    ShellStartupVerification,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    HomeRelativeDestination,
    WindowsPosixHomeDestination,
    WindowsPosixPackageDiscovery,
)

APPLICATION = Application(
    id="zsh",
    display_name="Zsh",
    platforms=(
        PlatformDeclaration(
            platform=Platform.LINUX,
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
                    source_leaf=".zshrc",
                    destination=HomeRelativeDestination(".zshrc"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    DpkgPackageDiscovery("zsh", executable_name="zsh"),
                    ExecutableDiscovery("zsh", ("--version",)),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ShellStartupVerification("zsh", "zsh", "main"),)
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
                    source_leaf=".zshrc",
                    destination=WindowsPosixHomeDestination(".zshrc"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WindowsPosixPackageDiscovery(
                        "zsh",
                        "zsh",
                        ("--version",),
                    ),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ShellStartupVerification("zsh", "zsh", "main"),)
            ),
        ),
    ),
)
