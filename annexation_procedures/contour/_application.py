from accumulated_instruments.machine_soul.model import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    HomeRelativeDestination,
    LocalAppDataRelativeDestination,
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
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.NOT_IMPLEMENTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf="contour.yml",
                    destination=HomeRelativeDestination(".config/contour/contour.yml"),
                ),
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
            Operation.CHECK_INSTALLED: Support.NOT_IMPLEMENTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf="contour.yml",
                    destination=LocalAppDataRelativeDestination("contour/contour.yml"),
                ),
            ),
        ),
    ),
)
