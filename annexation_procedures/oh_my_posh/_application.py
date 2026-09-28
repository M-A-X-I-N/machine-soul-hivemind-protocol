from annexation_procedures.model import (
    Application,
    ConfigurationVerificationPlan,
    ExecutableDiscovery,
    ConfigurationFile,
    Operation,
    Platform,
    PlatformDeclaration,
    Support,
    HomeRelativeDestination,
    InstallationDiscoveryPlan,
    InstallationScope,
    InstallationScopePolicy,
    LocalAppDataRelativeDestination,
    OhMyPoshVerification,
    WingetPackage,
    WingetPackageDiscovery,
)

APPLICATION = Application(
    id="oh_my_posh",
    display_name="Oh My Posh",
    platforms=(
        PlatformDeclaration(
            platform=Platform.LINUX,
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
                    name="theme",
                    source_leaf="theme.omp.json",
                    destination=HomeRelativeDestination(".config/oh-my-posh/theme.omp.json"),
                ),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (ExecutableDiscovery("oh-my-posh", ("version",)),)
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (
                    OhMyPoshVerification(
                        "oh-my-posh",
                        ("bash", "zsh", "fish"),
                    ),
                )
            ),
        ),
        PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={
            Operation.APPLY_CONFIG: Support.SUPPORTED,
            Operation.UNAPPLY_CONFIG: Support.SUPPORTED,
            Operation.CHECK_CONFIG: Support.SUPPORTED,
            Operation.VERIFY_CONFIG: Support.SUPPORTED,
            Operation.INSTALL: Support.SUPPORTED,
            Operation.UNINSTALL: Support.SUPPORTED,
            Operation.CHECK_INSTALLED: Support.SUPPORTED,
        },
            configurations=(
                ConfigurationFile(
                    name="theme",
                    source_leaf="theme.omp.json",
                    destination=LocalAppDataRelativeDestination("oh-my-posh/theme.omp.json"),
                ),
            ),
            install_strategy=WingetPackage(
                "JanDeDobbeleer.OhMyPosh",
                InstallationScopePolicy.required(InstallationScope.USER),
            ),
            installation_discovery=InstallationDiscoveryPlan(
                (
                    WingetPackageDiscovery(
                        "JanDeDobbeleer.OhMyPosh",
                        source="winget",
                        preferred=True,
                        executable_name="oh-my-posh.exe",
                        version_arguments=("version",),
                    ),
                    ExecutableDiscovery(
                        "oh-my-posh.exe",
                        ("version",),
                    ),
                )
            ),
            configuration_verification=ConfigurationVerificationPlan(
                (
                    OhMyPoshVerification(
                        "oh-my-posh.exe",
                        ("bash", "zsh", "fish", "powershell"),
                    ),
                )
            ),
        ),
    ),
)
