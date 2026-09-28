"""Shared read-only installation discovery engine."""

from __future__ import annotations

from dataclasses import replace
import shutil
from typing import Callable

from ..model import (
    DiscoveryObservation,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationAssessment,
    InstallationCandidate,
    InstallationOwnership,
    InstallationPresence,
    ObservationAuthority,
    OperationContext,
    PlatformDeclaration,
    TriState,
    WingetPackageDiscovery,
)
from ..process import ProcessResult, run_process
from ..state import InstallState, read_install_state


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]


def _preferred(value: bool) -> TriState:
    return TriState.YES if value else TriState.UNKNOWN


def _dpkg_candidate(
    strategy: DpkgPackageDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[InstallationCandidate | None, str | None]:
    if which("dpkg-query") is None:
        return None, "dpkg-query is unavailable."

    result = runner(["dpkg-query", "-W", "-f=$" + "{Status}", strategy.package_name])
    if result.returncode != 0 or "install ok installed" not in result.stdout:
        return None, None

    observation = DiscoveryObservation(
        "manager_registration",
        "dpkg",
        ObservationAuthority.DIRECT,
        {"package": strategy.package_name},
    )
    return InstallationCandidate(
        native_identity=strategy.package_name,
        registration_kind="dpkg",
        preferred_match=_preferred(strategy.preferred),
        manageable_by_preferred_strategy=_preferred(strategy.preferred),
        observations=(observation,),
    ), None


def _winget_candidate(
    strategy: WingetPackageDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[InstallationCandidate | None, str | None]:
    if which("winget") is None:
        return None, "winget is unavailable."

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
    if result.returncode != 0:
        return None, None

    observation = DiscoveryObservation(
        "catalog_correlation",
        "winget",
        ObservationAuthority.CORRELATED,
        {"package_id": strategy.package_id, "source": strategy.source},
    )
    return InstallationCandidate(
        native_identity=strategy.package_id,
        registration_kind="winget_correlation",
        preferred_match=_preferred(strategy.preferred),
        manageable_by_preferred_strategy=_preferred(strategy.preferred),
        observations=(observation,),
    ), None


def _executable_candidate(
    strategy: ExecutableDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[InstallationCandidate | None, str | None]:
    path = which(strategy.executable_name)
    if path is None:
        return None, None

    version = None
    observations = [
        DiscoveryObservation(
            "executable_path",
            "path",
            ObservationAuthority.DIRECT,
            {"executable": strategy.executable_name, "path": path},
        )
    ]

    if strategy.version_arguments:
        result = runner([path, *strategy.version_arguments])
        if result.returncode == 0:
            raw = result.stdout.strip() or result.stderr.strip()
            if raw:
                version = raw.splitlines()[0].strip()
                observations.append(
                    DiscoveryObservation(
                        "version_probe",
                        strategy.executable_name,
                        ObservationAuthority.DIRECT,
                        {"version_output": version},
                    )
                )

    return InstallationCandidate(
        native_identity=strategy.executable_name,
        version=version,
        paths=(path,),
        registration_kind="executable",
        preferred_match=_preferred(strategy.preferred),
        observations=tuple(observations),
    ), None


def _state_matches(state: InstallState, candidate: InstallationCandidate) -> bool:
    if state.identity != candidate.native_identity:
        return False
    if state.manager == "apt" and candidate.registration_kind == "dpkg":
        return True
    if state.manager == "winget" and candidate.registration_kind == "winget_correlation":
        return True
    return False


def discover_installation(
    application_id: str,
    declaration: PlatformDeclaration,
    context: OperationContext,
    *,
    runner: Runner = run_process,
    which: Which = shutil.which,
) -> InstallationAssessment:
    """Execute a declared read-only discovery plan and assess candidates."""
    plan = declaration.installation_discovery
    if plan is None:
        return InstallationAssessment(
            InstallationPresence.UNKNOWN,
            errors=("No installation discovery plan is declared.",),
        )

    candidates: list[InstallationCandidate] = []
    errors: list[str] = []

    for strategy in plan.strategies:
        if isinstance(strategy, DpkgPackageDiscovery):
            candidate, error = _dpkg_candidate(strategy, runner, which)
        elif isinstance(strategy, WingetPackageDiscovery):
            candidate, error = _winget_candidate(strategy, runner, which)
        elif isinstance(strategy, ExecutableDiscovery):
            candidate, error = _executable_candidate(strategy, runner, which)
        else:
            candidate, error = None, (
                f"Unsupported discovery strategy: {type(strategy).__name__}."
            )

        if candidate is not None:
            candidates.append(candidate)
        if error is not None:
            errors.append(error)

    state = read_install_state(context, application_id)
    state_relation = InstallationOwnership.UNKNOWN

    if state is not None:
        match_index = next(
            (
                index
                for index, candidate in enumerate(candidates)
                if _state_matches(state, candidate)
            ),
            None,
        )
        if match_index is None:
            state_relation = InstallationOwnership.STALE
        else:
            state_relation = InstallationOwnership.MANAGED
            candidates[match_index] = replace(
                candidates[match_index],
                ownership=InstallationOwnership.MANAGED,
            )
    elif candidates:
        state_relation = InstallationOwnership.UNMANAGED

    candidates = [
        candidate
        if candidate.ownership is InstallationOwnership.MANAGED
        else replace(candidate, ownership=InstallationOwnership.UNMANAGED)
        for candidate in candidates
    ]

    if len(candidates) > 1:
        presence = InstallationPresence.AMBIGUOUS
    elif candidates:
        presence = InstallationPresence.PRESENT
    elif errors:
        presence = InstallationPresence.UNKNOWN
    else:
        presence = InstallationPresence.ABSENT

    preferred_indexes = [
        index
        for index, candidate in enumerate(candidates)
        if candidate.preferred_match is TriState.YES
    ]
    preferred_index = preferred_indexes[0] if len(preferred_indexes) == 1 else None

    return InstallationAssessment(
        presence=presence,
        candidates=tuple(candidates),
        preferred_candidate_index=preferred_index,
        machine_soul_state=state_relation,
        errors=tuple(errors),
    )
