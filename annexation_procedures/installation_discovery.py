"""Shared read-only installation discovery engine."""

from __future__ import annotations

from dataclasses import replace
import shutil
from typing import Callable

from .model import (
    BuiltInExecutableDiscovery,
    DiscoveryObservation,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationAssessment,
    InstallationCandidate,
    InstallationOwnership,
    InstallationPresence,
    InstallationScope,
    ObservationAuthority,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TriState,
    WindowsAppxDiscovery,
    WindowsArpDiscovery,
    WingetPackageDiscovery,
)
from .process import ProcessResult, run_process
from .state import InstallState, read_install_state
from .windows_installation_discovery import (
    appx_candidates,
    arp_candidates,
    builtin_candidate,
)


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]


def _preferred(value: bool) -> TriState:
    return TriState.YES if value else TriState.UNKNOWN


def _dpkg_details(
    package_name: str,
    runner: Runner,
) -> tuple[str | None, str | None, str | None, bool]:
    format_string = (
        "$" + "{binary:Package}\t"
        + "$" + "{Version}\t"
        + "$" + "{Architecture}\t"
        + "$" + "{Status}"
    )
    result = runner(["dpkg-query", "-W", f"-f={format_string}", package_name])
    if result.returncode != 0:
        return None, None, None, False

    raw = result.stdout.strip()
    if "install ok installed" not in raw:
        return None, None, None, False

    fields = raw.split("\t")
    if len(fields) >= 4:
        binary_package, version, architecture = fields[:3]
        return (
            binary_package.strip() or package_name,
            version.strip() or None,
            architecture.strip() or None,
            True,
        )
    return package_name, None, None, True


def _dpkg_owner(path: str, runner: Runner, which: Which) -> str | None:
    if which("dpkg-query") is None:
        return None
    result = runner(["dpkg-query", "-S", path])
    if result.returncode != 0 or ":" not in result.stdout:
        return None
    owner = result.stdout.split(":", 1)[0].strip()
    return owner.split(":", 1)[0] if owner else None


def _dpkg_candidate(
    strategy: DpkgPackageDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[InstallationCandidate | None, str | None]:
    if which("dpkg-query") is None:
        return None, "dpkg-query is unavailable."

    binary_package, version, architecture, installed = _dpkg_details(
        strategy.package_name,
        runner,
    )
    if not installed:
        return None, None

    data: dict[str, object] = {"package": strategy.package_name}
    if binary_package:
        data["binary_package"] = binary_package
    if version:
        data["version"] = version
    if architecture:
        data["architecture"] = architecture

    observations = [
        DiscoveryObservation(
            "manager_registration",
            "dpkg",
            ObservationAuthority.DIRECT,
            data,
        )
    ]
    paths: tuple[str, ...] = ()

    if strategy.executable_name:
        path = which(strategy.executable_name)
        if path is not None:
            owner = _dpkg_owner(path, runner, which)
            if owner == strategy.package_name:
                paths = (path,)
                observations.append(
                    DiscoveryObservation(
                        "file_owner",
                        "dpkg",
                        ObservationAuthority.DIRECT,
                        {
                            "package": strategy.package_name,
                            "path": path,
                            "executable": strategy.executable_name,
                        },
                    )
                )

    return InstallationCandidate(
        native_identity=strategy.package_name,
        display_identity=binary_package,
        version=version,
        paths=paths,
        scope=InstallationScope.MACHINE,
        registration_kind="dpkg",
        preferred_match=_preferred(strategy.preferred),
        manageable_by_preferred_strategy=_preferred(strategy.preferred),
        observations=tuple(observations),
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

    data: dict[str, object] = {
        "package_id": strategy.package_id,
        "source": strategy.source,
    }
    if strategy.package_family_name:
        data["package_family_name"] = strategy.package_family_name

    observations = [
        DiscoveryObservation(
            "catalog_correlation",
            "winget",
            ObservationAuthority.CORRELATED,
            data,
        )
    ]
    paths: tuple[str, ...] = ()
    version = None

    if strategy.executable_name:
        path = which(strategy.executable_name)
        if path is not None:
            paths = (path,)
            observations.append(
                DiscoveryObservation(
                    "executable_path",
                    "winget",
                    ObservationAuthority.CORRELATED,
                    {
                        "executable": strategy.executable_name,
                        "path": path,
                    },
                )
            )
            if strategy.version_arguments:
                version_result = runner([path, *strategy.version_arguments])
                if version_result.returncode == 0:
                    raw = version_result.stdout.strip() or version_result.stderr.strip()
                    if raw:
                        version = raw.splitlines()[0].strip()
                        observations.append(
                            DiscoveryObservation(
                                "version_probe",
                                strategy.executable_name,
                                ObservationAuthority.CORRELATED,
                                {"version_output": version},
                            )
                        )

    return InstallationCandidate(
        native_identity=strategy.package_id,
        version=version,
        paths=paths,
        registration_kind="winget_correlation",
        preferred_match=_preferred(strategy.preferred),
        manageable_by_preferred_strategy=_preferred(strategy.preferred),
        observations=tuple(observations),
    ), None


def _executable_candidate(
    strategy: ExecutableDiscovery,
    context: OperationContext,
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

    native_identity = strategy.executable_name
    registration_kind = "executable"
    scope = InstallationScope.UNKNOWN

    if context.platform is Platform.LINUX:
        owner = _dpkg_owner(path, runner, which)
        if owner:
            native_identity = owner
            registration_kind = "dpkg"
            scope = InstallationScope.MACHINE
            observations.append(
                DiscoveryObservation(
                    "file_owner",
                    "dpkg",
                    ObservationAuthority.DIRECT,
                    {"package": owner, "path": path},
                )
            )
            _, package_version, _, installed = _dpkg_details(owner, runner)
            if installed and package_version:
                version = package_version

    return InstallationCandidate(
        native_identity=native_identity,
        version=version,
        paths=(path,),
        scope=scope,
        registration_kind=registration_kind,
        preferred_match=_preferred(strategy.preferred),
        observations=tuple(observations),
    ), None


def _candidate_identities(candidate: InstallationCandidate) -> set[str]:
    """Return only explicit cross-backend correlation identifiers."""
    identities: set[str] = set()
    for observation in candidate.observations:
        for key in ("package_id", "package_family_name", "product_code"):
            value = observation.data.get(key)
            if isinstance(value, str) and value:
                identities.add(value.casefold())
    return identities


def _candidate_executable_names(candidate: InstallationCandidate) -> set[str]:
    names: set[str] = set()
    for observation in candidate.observations:
        value = observation.data.get("executable")
        if isinstance(value, str) and value:
            names.add(value.casefold())
    return names


def _merge_pair(
    left: InstallationCandidate,
    right: InstallationCandidate,
) -> InstallationCandidate | None:
    left_paths = set(left.paths)
    right_paths = set(right.paths)
    same_registration = (
        left.registration_kind == right.registration_kind
        and left.native_identity.casefold() == right.native_identity.casefold()
    )
    correlated_identity = bool(_candidate_identities(left) & _candidate_identities(right))
    correlated_executable = bool(
        _candidate_executable_names(left)
        & _candidate_executable_names(right)
    ) and (
        left.registration_kind == "winget_correlation"
        or right.registration_kind == "winget_correlation"
    )
    if not (
        left_paths & right_paths
        or same_registration
        or correlated_identity
        or correlated_executable
    ):
        return None

    preferred = (
        TriState.YES
        if TriState.YES in {left.preferred_match, right.preferred_match}
        else (
            TriState.NO
            if left.preferred_match is TriState.NO and right.preferred_match is TriState.NO
            else TriState.UNKNOWN
        )
    )
    manageable = (
        TriState.YES
        if TriState.YES in {
            left.manageable_by_preferred_strategy,
            right.manageable_by_preferred_strategy,
        }
        else TriState.UNKNOWN
    )
    registration_kind = (
        left.registration_kind
        if left.registration_kind != "executable"
        else right.registration_kind
    )
    native_identity = (
        left.native_identity
        if left.registration_kind != "executable"
        else right.native_identity
    )

    paths = tuple(dict.fromkeys((*left.paths, *right.paths)))
    observations: list[DiscoveryObservation] = []
    for observation in (*left.observations, *right.observations):
        if observation not in observations:
            observations.append(observation)

    return InstallationCandidate(
        native_identity=native_identity,
        display_identity=left.display_identity or right.display_identity,
        version=left.version or right.version,
        paths=paths,
        scope=(
            left.scope
            if left.scope is not InstallationScope.UNKNOWN
            else right.scope
        ),
        registration_kind=registration_kind,
        acquisition_channel=left.acquisition_channel or right.acquisition_channel,
        acquisition_authority=left.acquisition_authority or right.acquisition_authority,
        preferred_match=preferred,
        manageable_by_preferred_strategy=manageable,
        ownership=left.ownership,
        uninstall_identity=left.uninstall_identity or right.uninstall_identity,
        observations=tuple(observations),
    )


def _merge_candidates(
    candidates: list[InstallationCandidate],
) -> list[InstallationCandidate]:
    merged: list[InstallationCandidate] = []
    for candidate in candidates:
        for index, existing in enumerate(merged):
            combined = _merge_pair(existing, candidate)
            if combined is not None:
                merged[index] = combined
                break
        else:
            merged.append(candidate)
    return merged

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
        found: list[InstallationCandidate] = []
        error: str | None = None

        if isinstance(strategy, DpkgPackageDiscovery):
            candidate, error = _dpkg_candidate(strategy, runner, which)
            if candidate is not None:
                found.append(candidate)
        elif isinstance(strategy, WingetPackageDiscovery):
            candidate, error = _winget_candidate(strategy, runner, which)
            if candidate is not None:
                found.append(candidate)
        elif isinstance(strategy, ExecutableDiscovery):
            candidate, error = _executable_candidate(
                strategy,
                context,
                runner,
                which,
            )
            if candidate is not None:
                found.append(candidate)
        elif isinstance(strategy, WindowsArpDiscovery):
            found, error = arp_candidates(strategy, which)
        elif isinstance(strategy, WindowsAppxDiscovery):
            found, error = appx_candidates(strategy, runner, which)
        elif isinstance(strategy, BuiltInExecutableDiscovery):
            candidate, error = builtin_candidate(strategy, runner, which)
            if candidate is not None:
                found.append(candidate)
        else:
            error = f"Unsupported discovery strategy: {type(strategy).__name__}."

        candidates.extend(found)
        if error is not None:
            errors.append(error)

    candidates = _merge_candidates(candidates)

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
        if match_index is not None:
            state_relation = InstallationOwnership.MANAGED
            candidates[match_index] = replace(
                candidates[match_index],
                ownership=InstallationOwnership.MANAGED,
            )
        elif errors and not candidates:
            state_relation = InstallationOwnership.UNKNOWN
        else:
            state_relation = InstallationOwnership.STALE
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
