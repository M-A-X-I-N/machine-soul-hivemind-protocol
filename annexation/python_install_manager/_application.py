from annexation.model import (
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
    id="python_install_manager",
    display_name="Python Install Manager",
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
                "9NQ7512CXL7T",
                InstallationScopePolicy.required(InstallationScope.USER),
                source="msstore",
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WingetPackageDiscovery(
                        "9NQ7512CXL7T",
                        source="msstore",
                        preferred=True,
                        executable_name="pymanager",
                    ),
                )
            ),
        ),
    ),
)
