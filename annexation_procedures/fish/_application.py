from annexation_procedures.model import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    AptPackage,
    HomeRelativeDestination,
    WindowsPosixHomeDestination,
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
                    source_leaf="config.fish",
                    destination=WindowsPosixHomeDestination(".config/fish/config.fish"),
                ),
            ),
        ),
    ),
)
