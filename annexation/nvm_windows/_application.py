from annexation.model import (
    Application,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
)

APPLICATION = Application(
    id="nvm_windows",
    display_name="NVM for Windows",
    platforms=(
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
                Operation.APPLY_CONFIG: Support.UNSUPPORTED,
                Operation.UNAPPLY_CONFIG: Support.UNSUPPORTED,
                Operation.CHECK_CONFIG: Support.UNSUPPORTED,
                Operation.VERIFY_CONFIG: Support.UNSUPPORTED,
                Operation.INSTALL: Support.NOT_IMPLEMENTED,
                Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
                Operation.CHECK_INSTALLED: Support.SUPPORTED,
            },
            installation_discovery=InstallationDiscoveryPlan(
                (
                    ExecutableDiscovery(
                        "nvm",
                        version_arguments=("version",),
                        preferred=True,
                    ),
                )
            ),
        ),
    ),
)
