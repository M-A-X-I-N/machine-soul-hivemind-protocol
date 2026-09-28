from annexation_procedures.model import (
    Application,
    BuiltInExecutableDiscovery,
    ConfigurationFile,
    InstallationDiscoveryPlan,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    CustomConfiguration,
    LocalAppDataRelativeDestination,
)
from annexation_procedures.cmd._configuration import handle_configuration

APPLICATION = Application(
    id="cmd",
    display_name="CMD",
    platforms=(
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
                    name="command_file",
                    source_leaf="cmdrc.cmd",
                    destination=LocalAppDataRelativeDestination("MachineSoul/cmd/cmdrc.cmd"),
                ),
            ),
            configuration_strategy=CustomConfiguration(handle_configuration),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    BuiltInExecutableDiscovery(
                        "cmd.exe",
                        "windows_cmd",
                        ("/d", "/c", "ver"),
                    ),
                )
            ),
        ),
    ),
)
