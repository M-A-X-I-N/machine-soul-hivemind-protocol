from accumulated_instruments.machine_soul.model import (
    Application,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    PowerShellProfileDestination,
)

APPLICATION = Application(
    id="powershell",
    display_name="PowerShell",
    platforms=(
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
                    name="profile",
                    source_leaf="Microsoft.PowerShell_profile.ps1",
                    destination=PowerShellProfileDestination(),
                ),
            ),
        ),
    ),
)
