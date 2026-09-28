from annexation_procedures.model import (
    Application,
    InstallationDiscoveryPlan,
    InstallationScope,
    InstallationScopePolicy,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    WingetPackage,
    WingetPackageDiscovery,
)

APPLICATION = Application(
    id="jetbrains_toolbox",
    display_name="JetBrains Toolbox",
    platforms=(
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
                Operation.APPLY_CONFIG: Support.UNSUPPORTED,
                Operation.UNAPPLY_CONFIG: Support.UNSUPPORTED,
                Operation.CHECK_CONFIG: Support.UNSUPPORTED,
                Operation.VERIFY_CONFIG: Support.UNSUPPORTED,
                Operation.INSTALL: Support.SUPPORTED,
                Operation.UNINSTALL: Support.SUPPORTED,
                Operation.CHECK_INSTALLED: Support.SUPPORTED,
            },
            install_strategy=WingetPackage(
                "JetBrains.Toolbox",
                InstallationScopePolicy.required(InstallationScope.USER),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WingetPackageDiscovery(
                        "JetBrains.Toolbox",
                        preferred=True,
                    ),
                )
            ),
        ),
    ),
)
