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
    InstallationCandidate,
    InstallationOwnership,
    InstallationPresence,
    InstallationScope,
    InstallationScopePolicy,
    OperationContext,
    OperationResult,
    PlatformDeclaration,
    RemoteInstallScript,
    StandaloneBinary,
    WingetPackage,
    installation_scope_target_error,
)
from ..installation_ownership import (
    candidate_satisfies_scope_policy,
    installation_candidate_matches_state,
    state_satisfies_scope_policy,
)
from ..process import ProcessResult, run_process
from ..state import (
    InstallState,
    delete_scoped_install_state,
    read_install_states,
    read_legacy_install_state,
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


def _scope_policy(strategy: object) -> InstallationScopePolicy | None:
    policy = getattr(strategy, "scope_policy", None)
    return policy if isinstance(policy, InstallationScopePolicy) else None


def _scope_result_data(policy: InstallationScopePolicy) -> dict[str, object]:
    return {
        "scope_policy": policy.mode.value,
        "requested_scope": policy.scope.value if policy.scope else None,
    }


def _scope_guard(
    strategy: object,
    context: OperationContext,
) -> tuple[InstallationScopePolicy | None, OperationResult | None]:
    policy = _scope_policy(strategy)
    if policy is None:
        return None, OperationResult.not_implemented(
            "installation_scope_policy_missing",
            "Installation strategy does not declare a scope policy.",
        )
    error = installation_scope_target_error(policy, context.target_account)
    if error is not None:
        return policy, OperationResult.unsupported(
            "installation_scope_target_unsupported",
            error,
            data={
                **_scope_result_data(policy),
                "target_account": context.target_account.name,
            },
        )
    return policy, None


def _intended_candidates(
    candidates: tuple[InstallationCandidate, ...],
    policy: InstallationScopePolicy,
    context: OperationContext,
) -> list[InstallationCandidate]:
    return [
        candidate
        for candidate in candidates
        if candidate_satisfies_scope_policy(
            candidate,
            policy,
            context.target_account,
        )
    ]


def _intended_states(
    states: tuple[InstallState, ...],
    policy: InstallationScopePolicy,
    context: OperationContext,
) -> list[InstallState]:
    return [
        state
        for state in states
        if state_satisfies_scope_policy(
            state,
            policy,
            context.target_account,
        )
    ]


def _state_from_candidate(
    application: Application,
    strategy: object,
    policy: InstallationScopePolicy,
    candidate: InstallationCandidate,
    context: OperationContext,
) -> InstallState:
    manager, identity, metadata = _manager_identity(strategy)
    if candidate.registration_kind is not None:
        metadata["registration_kind"] = candidate.registration_kind
    return InstallState(
        application=application.id,
        host=context.host,
        account=context.target_account.name,
        manager=manager,
        identity=identity,
        requested_scope_mode=policy.mode,
        requested_scope=policy.scope,
        actual_scope=candidate.scope,
        scope_subject=(
            candidate.scope_subject
            if candidate.scope in {InstallationScope.USER, InstallationScope.PACKAGE_USER}
            else None
        ),
        native_identity=candidate.native_identity,
        uninstall_identity=candidate.uninstall_identity,
        metadata=metadata,
    )


def _scoped_result(
    result: OperationResult,
    policy: InstallationScopePolicy,
    *,
    candidate: InstallationCandidate | None = None,
) -> OperationResult:
    data = dict(result.data)
    data.update(_scope_result_data(policy))
    if candidate is not None:
        data["candidate"] = candidate.to_dict()
    return OperationResult(
        result.status,
        result.changed,
        result.code,
        result.message,
        data,
    )


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

    policy, guard = _scope_guard(strategy, context)
    if guard is not None:
        return guard
    assert policy is not None

    legacy_state = read_legacy_install_state(context, application.id)
    if legacy_state is not None:
        assessment = discover_installation(
            application.id,
            declaration,
            context,
            runner=runner,
            which=which,
        )
        return OperationResult.failure(
            "installation_provenance_unreconciled",
            "Scope-unknown legacy installation provenance must be reconciled before mutation.",
            data={
                **_scope_result_data(policy),
                "assessment": assessment.to_dict(),
                "legacy_manager": legacy_state.manager,
                "legacy_identity": legacy_state.identity,
            },
        )

    assessment = discover_installation(
        application.id,
        declaration,
        context,
        runner=runner,
        which=which,
    )
    intended = _intended_candidates(assessment.candidates, policy, context)
    relevant_states = _intended_states(
        read_install_states(context, application.id),
        policy,
        context,
    )

    if len(intended) > 1:
        return OperationResult.failure(
            "installed_ambiguous",
            "Multiple candidates exist in the intended installation scope; refusing mutation.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )
    if len(intended) == 1:
        candidate = intended[0]
        if candidate.ownership is InstallationOwnership.MANAGED:
            return OperationResult.success(
                "installed_managed",
                "The intended scoped installation is already owned by Machine-Soul.",
                data={
                    **_scope_result_data(policy),
                    "assessment": assessment.to_dict(),
                    "candidate": candidate.to_dict(),
                },
            )
        return OperationResult.failure(
            "installed_unmanaged",
            "An installation already exists in the intended scope but is unmanaged; refusing to claim it.",
            data={
                **_scope_result_data(policy),
                "assessment": assessment.to_dict(),
                "candidate": candidate.to_dict(),
            },
        )

    if relevant_states:
        return OperationResult.failure(
            "installation_provenance_stale",
            "Scoped Machine-Soul provenance exists without a matching current candidate; refusing install until reconciled.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )

    if assessment.presence is InstallationPresence.UNKNOWN and not assessment.candidates:
        return OperationResult.error(
            "installation_unknown",
            "Installation presence could not be determined safely before mutation.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
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
        return _scoped_result(result, policy)

    post = discover_installation(
        application.id,
        declaration,
        context,
        runner=runner,
        which=which,
    )
    verified = _intended_candidates(post.candidates, policy, context)
    if len(verified) != 1:
        return OperationResult.error(
            (
                "installation_scope_ambiguous"
                if len(verified) > 1
                else "installation_scope_unverified"
            ),
            (
                "Installation changed state but multiple intended-scope candidates were discovered."
                if len(verified) > 1
                else "Installation changed state but the intended scope could not be verified."
            ),
            changed=True,
            data={**_scope_result_data(policy), "assessment": post.to_dict()},
        )

    candidate = verified[0]
    if candidate.ownership is InstallationOwnership.MANAGED:
        return OperationResult.success(
            "installed_managed",
            "Installation completed and existing exact scoped ownership is valid.",
            changed=True,
            data={
                **_scope_result_data(policy),
                "assessment": post.to_dict(),
                "candidate": candidate.to_dict(),
            },
        )

    state = _state_from_candidate(
        application,
        strategy,
        policy,
        candidate,
        context,
    )
    try:
        write_install_state(context, state)
    except Exception as exc:
        return OperationResult.error(
            "provenance_write_failed",
            f"Application installed but scoped provenance could not be recorded: {exc}",
            changed=True,
            data={**_scope_result_data(policy), "candidate": candidate.to_dict()},
        )

    return OperationResult.success(
        "installed_managed",
        "Application was installed and exact scoped Machine-Soul provenance was recorded.",
        changed=True,
        data={
            **_scope_result_data(policy),
            "candidate": candidate.to_dict(),
        },
    )



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

    policy, guard = _scope_guard(strategy, context)
    if guard is not None:
        return guard
    assert policy is not None

    legacy_state = read_legacy_install_state(context, application.id)
    if legacy_state is not None:
        assessment = discover_installation(
            application.id,
            declaration,
            context,
            runner=runner,
            which=which,
        )
        return OperationResult.failure(
            "installation_provenance_unreconciled",
            "Scope-unknown legacy installation provenance cannot authorize uninstall.",
            data={
                **_scope_result_data(policy),
                "assessment": assessment.to_dict(),
                "legacy_manager": legacy_state.manager,
                "legacy_identity": legacy_state.identity,
            },
        )

    states = _intended_states(
        read_install_states(context, application.id),
        policy,
        context,
    )
    assessment = discover_installation(
        application.id,
        declaration,
        context,
        runner=runner,
        which=which,
    )
    intended = _intended_candidates(assessment.candidates, policy, context)

    if not states:
        if intended:
            return OperationResult.failure(
                "installed_unmanaged",
                "An installation exists in the intended scope without Machine-Soul ownership; refusing uninstall.",
                data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
            )
        if assessment.presence is InstallationPresence.UNKNOWN and not assessment.candidates:
            return OperationResult.error(
                "installation_unknown",
                "Installation presence could not be determined safely.",
                data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
            )
        return OperationResult.success(
            "not_installed",
            "No Machine-Soul-owned installation exists in the intended scope.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )

    if len(states) > 1:
        return OperationResult.failure(
            "installation_provenance_ambiguous",
            "Multiple ownership records satisfy the intended scope; refusing uninstall.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )

    state = states[0]
    matches = [
        candidate
        for candidate in assessment.candidates
        if installation_candidate_matches_state(state, candidate)
    ]
    if len(matches) > 1:
        return OperationResult.failure(
            "installed_ambiguous",
            "One ownership record matches multiple current candidates; refusing uninstall.",
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )

    if not matches:
        if assessment.presence is InstallationPresence.UNKNOWN and not assessment.candidates:
            return OperationResult.error(
                "installation_unknown",
                "Installation presence could not be determined safely; ownership was preserved.",
                data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
            )
        if context.dry_run:
            return OperationResult.success(
                "would_clear_stale_provenance",
                "The exact owned candidate is absent; stale scoped provenance would be removed.",
                data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
            )
        delete_scoped_install_state(context, state)
        return OperationResult.success(
            "not_installed",
            "The exact owned candidate was absent and stale scoped provenance was removed.",
            changed=True,
            data={**_scope_result_data(policy), "assessment": assessment.to_dict()},
        )

    candidate = matches[0]
    result = _perform_strategy(
        strategy,
        uninstall=True,
        application=application,
        context=context,
        runner=runner,
        which=which,
        geteuid=geteuid,
    )
    if result.status.value != "success" or context.dry_run:
        return _scoped_result(result, policy, candidate=candidate)

    post = discover_installation(
        application.id,
        declaration,
        context,
        runner=runner,
        which=which,
    )
    if any(
        installation_candidate_matches_state(state, item)
        for item in post.candidates
    ):
        return OperationResult.error(
            "verification_failed",
            "Backend removal returned success but the exact owned candidate is still present.",
            changed=True,
            data={**_scope_result_data(policy), "assessment": post.to_dict()},
        )

    try:
        delete_scoped_install_state(context, state)
    except Exception as exc:
        return OperationResult.error(
            "provenance_cleanup_failed",
            f"Application was removed but scoped provenance could not be deleted: {exc}",
            changed=True,
            data={**_scope_result_data(policy), "candidate": candidate.to_dict()},
        )

    return OperationResult.success(
        "not_installed",
        "The exact Machine-Soul-owned scoped installation was removed.",
        changed=True,
        data={
            **_scope_result_data(policy),
            "candidate": candidate.to_dict(),
        },
    )
