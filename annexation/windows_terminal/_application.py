from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    ConfigurationFile,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    Operation,
    ResolvedPathVerification,
    Platform,
    PlatformDeclaration,
    Support,
    WindowsAppxDiscovery,
    WindowsTerminalSettingsDestination,
    WingetPackageDiscovery,
)

APPLICATION = Application(
    id="windows_terminal",
    display_name="Windows Terminal",
    platforms=(
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
                    name="settings",
                    source_leaf="settings.json",
                    destination=WindowsTerminalSettingsDestination(),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WingetPackageDiscovery(
                        "Microsoft.WindowsTerminal",
                        executable_name="wt.exe",
                        package_family_name="Microsoft.WindowsTerminal_8wekyb3d8bbwe",
                    ),
                    WindowsAppxDiscovery(
                        "Microsoft.WindowsTerminal_8wekyb3d8bbwe",
                        executable_name="wt.exe",
                    ),
                    ExecutableDiscovery("wt.exe"),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ResolvedPathVerification("settings", "wt.exe"),)
            ),
        ),
    ),
)
