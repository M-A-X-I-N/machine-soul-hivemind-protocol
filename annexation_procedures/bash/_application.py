from annexation_procedures.model import (
    Application,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
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
    id="bash",
    display_name="Bash",
    platforms=(
        PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf=".bashrc",
                    destination=HomeRelativeDestination(".bashrc"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    DpkgPackageDiscovery("bash", executable_name="bash"),
                    ExecutableDiscovery("bash", ("--version",)),
                )
            ),
        ),
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf=".bashrc",
                    destination=WindowsPosixHomeDestination(".bashrc"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WindowsPosixPackageDiscovery(
                        "bash",
                        "bash",
                        ("--version",),
                    ),
                )
            ),
        ),
    ),
)
