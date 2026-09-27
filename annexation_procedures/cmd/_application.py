from accumulated_instruments.machine_soul.model import (
    Application,
    ConfigurationFile,
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
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.NOT_IMPLEMENTED,
        },
            configurations=(
                ConfigurationFile(
                    name="command_file",
                    source_leaf="cmdrc.cmd",
                    destination=LocalAppDataRelativeDestination("MachineSoul/cmd/cmdrc.cmd"),
                ),
            ),
            configuration_strategy=CustomConfiguration(handle_configuration),
        ),
    ),
)
