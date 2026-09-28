"""Generic installation/check/uninstall engines and strategy handlers."""

from __future__ import annotations

import os
import shutil
from typing import Callable

from ..installation_discovery import discover_installation
from ..model import (
    Application,
    AptPackage,
    CustomInstaller,
    InstallationOwnership,
    InstallationPresence,
    OperationContext,
    OperationResult,
    PlatformDeclaration,
    RemoteInstallScript,
    StandaloneBinary,
    WingetPackage,
    installation_scope_target_error,
)
from ..process import ProcessResult, run_process
from ..state import (
    InstallState,
    delete_install_state,
    read_install_state,
    write_install_state,
)


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]
GetEuid = Callable[[], int]


def _default_geteuid() -> int:
    return os.geteuid() if hasattr(os, "geteuid") else 1


def _apt_installed(strategy: AptPackage, runner: Runner) -> bool:
    result = runner(["dpkg-query", "-W", "-f=${Status}", strategy.package_name])
    return result.returncode == 0 and "install ok installed" in result.stdout


def _winget_installed(strategy: WingetPackage, runner: Runner) -> bool:
    result = runner(
        [
            "winget",
            "list",
            "--id",
            strategy.package_id,
            "--source",
            strategy.source,
            "--exact",
            "--disable-interactivity",
        ]
    )
    return result.returncode == 0


def _is_installed(strategy: object, runner: Runner) -> bool | None:
    if isinstance(strategy, AptPackage):
        return _apt_installed(strategy, runner)
    if isinstance(strategy, WingetPackage):
        return _winget_installed(strategy, runner)
    return None


def _manager_identity(strategy: object) -> tuple[str, str, dict[str, object]]:
    if isinstance(strategy, AptPackage):
        return "apt", strategy.package_name, {}
    if isinstance(strategy, WingetPackage):
        return "winget", strategy.package_id, {"source": strategy.source}
    return type(strategy).__name__.lower(), type(strategy).__name__, {}


def check_installed(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    *,
    runner: Runner = run_process,
    which: Which | None = None,
) -> OperationResult:
    assessment = discover_installation(
        application.id,
        declaration,
        context,
        runner=runner,
        which=which,
    )
    data = {
        "application": application.id,
        "assessment": assessment.to_dict(),
    }

    if assessment.presence is InstallationPresence.PRESENT:
        if assessment.machine_soul_state is InstallationOwnership.MANAGED:
            return OperationResult.success(
                "installed_managed",
                "Application is installed with matching Machine-Soul provenance.",
                data=data,
            )
        return OperationResult.failure(
            "installed_unmanaged",
            "Application is installed but is not owned by Machine-Soul.",
            data=data,
        )

    if assessment.presence is InstallationPresence.AMBIGUOUS:
        return OperationResult.failure(
            "installed_ambiguous",
            "Multiple or conflicting installation candidates were discovered.",
            data=data,
        )

    if assessment.presence is InstallationPresence.UNKNOWN:
        return OperationResult.error(
            "installation_unknown",
            "Installation presence could not be determined safely.",
            data=data,
        )

    return OperationResult.failure(
        "not_installed",
        "Application is not installed according to the declared discovery plan.",
        data=data,
    )

def _apt_prefix(
    *,
    which: Which,
    geteuid: GetEuid,
) -> list[str] | OperationResult:
    if which("apt-get") is None or which("dpkg-query") is None:
        return OperationResult.unsupported(
            "apt_unavailable",
            "apt-get/dpkg-query are not available on this environment.",
        )
    if geteuid() == 0:
        return []
    if which("sudo") is not None:
        return ["sudo"]
    return OperationResult.error(
        "permission_denied",
        "apt installation requires root privileges or sudo.",
    )


def _perform_apt(
    strategy: AptPackage,
    *,
    uninstall: bool,
    context: OperationContext,
    runner: Runner,
    which: Which,
    geteuid: GetEuid,
) -> OperationResult:
    prefix = _apt_prefix(which=which, geteuid=geteuid)
    if isinstance(prefix, OperationResult):
        return prefix

    verb = "remove" if uninstall else "install"
    argv = [*prefix, "apt-get", verb, "-y", strategy.package_name]
    if context.dry_run:
        return OperationResult.success(
            "would_uninstall" if uninstall else "would_install",
            f"apt package {strategy.package_name!r} would be {verb}ed.",
            data={"argv": argv},
        )

    result = runner(argv)
    if result.returncode != 0:
        return OperationResult.error(
            "package_manager_failed",
            f"apt-get {verb} failed with exit code {result.returncode}.",
            data={"stderr": result.stderr[-2000:]},
        )

    installed_after = _apt_installed(strategy, runner)
    if uninstall and installed_after:
        return OperationResult.error(
            "verification_failed",
            "apt removal returned success but the package still reports installed.",
            changed=True,
        )
    if not uninstall and not installed_after:
        return OperationResult.error(
            "verification_failed",
            "apt installation returned success but the package does not report installed.",
            changed=True,
        )

    return OperationResult.success(
        "not_installed" if uninstall else "installed_managed",
        "apt package was removed." if uninstall else "apt package was installed.",
        changed=True,
    )


def _perform_winget(
    strategy: WingetPackage,
    *,
    uninstall: bool,
    context: OperationContext,
    runner: Runner,
    which: Which,
) -> OperationResult:
    if which("winget") is None:
        return OperationResult.unsupported("winget_unavailable", "WinGet is not available.")

    if uninstall:
        argv = [
            "winget",
            "uninstall",
            "--id",
            strategy.package_id,
            "--source",
            strategy.source,
            "--exact",
            "--disable-interactivity",
        ]
    else:
        argv = [
            "winget",
            "install",
            "--id",
            strategy.package_id,
            "--source",
            strategy.source,
            "--exact",
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--disable-interactivity",
        ]

    if context.dry_run:
        return OperationResult.success(
            "would_uninstall" if uninstall else "would_install",
            f"WinGet package {strategy.package_id!r} would be {'removed' if uninstall else 'installed'}.",
            data={"argv": argv},
        )

    result = runner(argv)
    if result.returncode != 0:
        return OperationResult.error(
            "package_manager_failed",
            f"WinGet {'uninstall' if uninstall else 'install'} failed with exit code {result.returncode}.",
            data={"stderr": result.stderr[-2000:]},
        )

    installed_after = _winget_installed(strategy, runner)
    if uninstall and installed_after:
        return OperationResult.error(
            "verification_failed",
            "WinGet removal returned success but the package still reports installed.",
            changed=True,
        )
    if not uninstall and not installed_after:
        return OperationResult.error(
            "verification_failed",
            "WinGet installation returned success but the package does not report installed.",
            changed=True,
        )

    return OperationResult.success(
        "not_installed" if uninstall else "installed_managed",
        "WinGet package was removed." if uninstall else "WinGet package was installed.",
        changed=True,
    )


def _perform_strategy(
    strategy: object,
    *,
    uninstall: bool,
    application: Application,
    context: OperationContext,
    runner: Runner,
    which: Which,
    geteuid: GetEuid,
) -> OperationResult:
    if isinstance(strategy, AptPackage):
        return _perform_apt(
            strategy,
            uninstall=uninstall,
            context=context,
            runner=runner,
            which=which,
            geteuid=geteuid,
        )
    if isinstance(strategy, WingetPackage):
        return _perform_winget(
            strategy,
            uninstall=uninstall,
            context=context,
            runner=runner,
            which=which,
        )
    if isinstance(strategy, CustomInstaller):
        if uninstall:
            return OperationResult.not_implemented(
                "custom_uninstall_not_declared",
                "CustomInstaller does not implicitly define uninstall behavior.",
            )
        result = strategy.handler(application, context)
        if not isinstance(result, OperationResult):
            raise TypeError("CustomInstaller handler must return OperationResult.")
        return result
    if isinstance(strategy, (RemoteInstallScript, StandaloneBinary)):
        return OperationResult.not_implemented(
            "installation_strategy_not_implemented",
            f"Shared handler for {type(strategy).__name__} is not implemented yet.",
        )
    return OperationResult.not_implemented(
        "installation_strategy_not_implemented",
        f"Unknown installation strategy type: {type(strategy).__name__}.",
    )


def install_application(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    *,
    runner: Runner = run_process,
    which: Which = shutil.which,
    geteuid: GetEuid = _default_geteuid,
) -> OperationResult:
    strategy = declaration.install_strategy
    if strategy is None:
        return OperationResult.not_implemented(
            "installation_strategy_missing",
            "No installation strategy is declared for this platform.",
        )

    scope_policy = getattr(strategy, "scope_policy", None)
    if scope_policy is not None:
        scope_error = installation_scope_target_error(
            scope_policy,
            context.target_account,
        )
        if scope_error is not None:
            return OperationResult.unsupported(
                "installation_scope_target_unsupported",
                scope_error,
                data={
                    "scope_policy": scope_policy.mode.value,
                    "scope": scope_policy.scope.value if scope_policy.scope else None,
                    "target_account": context.target_account.name,
                },
            )

    scope_policy = getattr(strategy, "scope_policy", None)
    if scope_policy is not None:
        scope_error = installation_scope_target_error(
            scope_policy,
            context.target_account,
        )
        if scope_error is not None:
            return OperationResult.unsupported(
                "installation_scope_target_unsupported",
                scope_error,
                data={
                    "scope_policy": scope_policy.mode.value,
                    "scope": scope_policy.scope.value if scope_policy.scope else None,
                    "target_account": context.target_account.name,
                },
            )

    installed = _is_installed(strategy, runner)
    if installed is True:
        if read_install_state(context, application.id) is not None:
            return OperationResult.success(
                "installed_managed",
                "Application is already installed with Machine-Soul provenance.",
            )
        return OperationResult.failure(
            "installed_unmanaged",
            "Application is already installed but is unmanaged; refusing to claim ownership.",
        )

    result = _perform_strategy(
        strategy,
        uninstall=False,
        application=application,
        context=context,
        runner=runner,
        which=which,
        geteuid=geteuid,
    )
    if result.status.value != "success" or not result.changed:
        return result

    manager, identity, metadata = _manager_identity(strategy)
    state = InstallState(
        application=application.id,
        host=context.host,
        account=context.target_account.name,
        manager=manager,
        identity=identity,
        metadata=metadata,
    )
    try:
        write_install_state(context, state)
    except Exception as exc:
        return OperationResult.error(
            "provenance_write_failed",
            f"Application installed but provenance could not be recorded: {exc}",
            changed=True,
        )
    return result


def uninstall_application(
    application: Application,
    declaration: PlatformDeclaration,
    context: OperationContext,
    *,
    runner: Runner = run_process,
    which: Which = shutil.which,
    geteuid: GetEuid = _default_geteuid,
) -> OperationResult:
    strategy = declaration.install_strategy
    if strategy is None:
        return OperationResult.not_implemented(
            "installation_strategy_missing",
            "No installation strategy is declared for this platform.",
        )

    state = read_install_state(context, application.id)
    installed = _is_installed(strategy, runner)

    if state is None:
        if installed:
            return OperationResult.failure(
                "installed_unmanaged",
                "Application is installed without Machine-Soul provenance; refusing to uninstall.",
            )
        return OperationResult.success("not_installed", "Application is already not installed.")

    if installed is False:
        if context.dry_run:
            return OperationResult.success(
                "would_clear_stale_provenance",
                "Application is absent; stale install provenance would be removed.",
            )
        delete_install_state(context, application.id)
        return OperationResult.success(
            "not_installed",
            "Application was absent and stale provenance was removed.",
            changed=True,
        )

    result = _perform_strategy(
        strategy,
        uninstall=True,
        application=application,
        context=context,
        runner=runner,
        which=which,
        geteuid=geteuid,
    )
    if result.status.value != "success":
        return result
    if context.dry_run:
        return result

    try:
        delete_install_state(context, application.id)
    except Exception as exc:
        return OperationResult.error(
            "provenance_cleanup_failed",
            f"Application was removed but install provenance could not be deleted: {exc}",
            changed=True,
        )
    return result
