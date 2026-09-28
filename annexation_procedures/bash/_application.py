from annexation_procedures.model import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    HomeRelativeDestination,
    WindowsPosixHomeDestination,
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
            Operation.CHECK_INSTALLED: Support.NOT_IMPLEMENTED,
        },
            configurations=(
                ConfigurationFile(
                    name="main",
                    source_leaf=".bashrc",
                    destination=HomeRelativeDestination(".bashrc"),
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
                    source_leaf=".bashrc",
                    destination=WindowsPosixHomeDestination(".bashrc"),
                ),
            ),
        ),
    ),
)
