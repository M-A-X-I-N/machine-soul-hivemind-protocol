from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    BuiltInExecutableDiscovery,
    ConfigurationFile,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    PowerShellProfileDestination,
    ResolvedPathVerification,
    WindowsAppxDiscovery,
    WindowsArpDiscovery,
    WingetPackageDiscovery,
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
            Operation.VERIFY_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.NOT_IMPLEMENTED,
            Operation.UNINSTALL: Support.NOT_IMPLEMENTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="profile",
                    source_leaf="Microsoft.PowerShell_profile.ps1",
                    destination=PowerShellProfileDestination(),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WingetPackageDiscovery(
                        "Microsoft.PowerShell",
                        executable_name="pwsh.exe",
                        version_arguments=(
                            "-NoProfile",
                            "-Command",
                            "$PSVersionTable.PSVersion.ToString()",
                        ),
                        package_family_name="Microsoft.PowerShell_8wekyb3d8bbwe",
                    ),
                    WindowsAppxDiscovery(
                        "Microsoft.PowerShell_8wekyb3d8bbwe",
                        executable_name="pwsh.exe",
                    ),
                    WindowsArpDiscovery(executable_name="pwsh.exe"),
                    ExecutableDiscovery(
                        "pwsh.exe",
                        (
                            "-NoProfile",
                            "-Command",
                            "$PSVersionTable.PSVersion.ToString()",
                        ),
                    ),
                    BuiltInExecutableDiscovery(
                        "powershell.exe",
                        "windows_powershell",
                        (
                            "-NoProfile",
                            "-Command",
                            "$PSVersionTable.PSVersion.ToString()",
                        ),
                    ),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (ResolvedPathVerification("profile"),)
            ),
        ),
    ),
)
