from annexation_procedures.model import (
    Application,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    HomeRelativeDestination,
    LocalAppDataRelativeDestination,
    WindowsArpDiscovery,
)

APPLICATION = Application(
    id="contour",
    display_name="Contour",
    platforms=(
        PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.VERIFY_CONFIG: Support.NOT_IMPLEMENTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf="contour.yml",
                    destination=HomeRelativeDestination(".config/contour/contour.yml"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (ExecutableDiscovery("contour", ("--version",)),)
            ),
        ),
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.VERIFY_CONFIG: Support.NOT_IMPLEMENTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf="contour.yml",
                    destination=LocalAppDataRelativeDestination("contour/contour.yml"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WindowsArpDiscovery(executable_name="contour.exe"),
                    ExecutableDiscovery("contour.exe", ("--version",)),
                )
            ),
        ),
    ),
)
