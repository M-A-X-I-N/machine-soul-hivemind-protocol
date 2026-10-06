"""Windows POSIX compatibility-environment installation discovery."""

from __future__ import annotations

from dataclasses import dataclass
import ntpath
from typing import Callable

from .model import (
    DiscoveryObservation,
    InstallationCandidate,
    InstallationScope,
    ObservationAuthority,
    OperationContext,
    WindowsPosixPackageDiscovery,
)
from .process import ProcessResult


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]


@dataclass(frozen=True)
class WindowsPosixEnvironment:
    kind: str
    root: str
    uname: str
    msystem: str | None

    @property
    def identity(self) -> str:
        return f"{self.kind}:{ntpath.normcase(ntpath.normpath(self.root))}"


def _within(path: str, directory: str) -> bool:
    path_norm = ntpath.normcase(ntpath.normpath(path))
    dir_norm = ntpath.normcase(ntpath.normpath(directory))
    try:
        return ntpath.commonpath((path_norm, dir_norm)) == dir_norm
    except ValueError:
        return False


def discover_windows_posix_environment(
    context: OperationContext,
    runner: Runner,
    which: Which,
) -> tuple[WindowsPosixEnvironment | None, str | None]:
    cygpath = which("cygpath")
    uname = which("uname")
    if cygpath is None or uname is None:
        return None, "Windows POSIX discovery requires cygpath and uname from the active environment."

    uname_result = runner([uname, "-s"])
    root_result = runner([cygpath, "-w", "/"])
    if uname_result.returncode != 0 or not uname_result.stdout.strip():
        return None, "Unable to identify the active Windows POSIX environment with uname."
    if root_result.returncode != 0 or not root_result.stdout.strip():
        return None, "Unable to resolve the active Windows POSIX environment root with cygpath."

    uname_text = uname_result.stdout.strip().splitlines()[0]
    upper = uname_text.upper()
    if upper.startswith("CYGWIN"):
        kind = "cygwin"
    elif upper.startswith(("MSYS", "MINGW")):
        kind = "msys2_style"
    else:
        return None, f"Unsupported Windows POSIX uname identity: {uname_text!r}."

    return (
        WindowsPosixEnvironment(
            kind=kind,
            root=root_result.stdout.strip().splitlines()[0],
            uname=uname_text,
            msystem=context.environment.get("MSYSTEM"),
        ),
        None,
    )


def _msys2_package(
    package_name: str,
    runner: Runner,
    which: Which,
) -> tuple[str | None, str | None]:
    pacman = which("pacman")
    if pacman is None:
        return None, "pacman is unavailable in the active MSYS2-style environment."
    result = runner([pacman, "-Q", package_name])
    if result.returncode != 0:
        return None, None
    fields = result.stdout.strip().split()
    if not fields or fields[0] != package_name:
        return None, f"pacman returned an unexpected record for {package_name!r}."
    return (fields[1] if len(fields) > 1 else None), None


def _cygwin_package(
    package_name: str,
    runner: Runner,
    which: Which,
) -> tuple[str | None, str | None]:
    cygcheck = which("cygcheck")
    if cygcheck is None:
        return None, "cygcheck is unavailable in the active Cygwin environment."
    result = runner([cygcheck, "-c", "-d", package_name])
    if result.returncode != 0:
        return None, None

    for line in result.stdout.splitlines():
        fields = line.split()
        if fields and fields[0] == package_name:
            return (fields[1] if len(fields) > 1 else None), None
    return None, None


def windows_posix_candidates(
    strategy: WindowsPosixPackageDiscovery,
    context: OperationContext,
    runner: Runner,
    which: Which,
) -> tuple[list[InstallationCandidate], str | None]:
    environment, environment_error = discover_windows_posix_environment(
        context,
        runner,
        which,
    )
    if environment is None:
        return [], environment_error

    executable = which(strategy.executable_name)
    executable_in_environment = bool(
        executable and _within(executable, environment.root)
    )

    if environment.kind == "cygwin":
        package_version, package_error = _cygwin_package(
            strategy.package_name,
            runner,
            which,
        )
        registration_kind = "cygwin_package"
        manager = "cygcheck"
    else:
        package_version, package_error = _msys2_package(
            strategy.package_name,
            runner,
            which,
        )
        registration_kind = "msys2_package"
        manager = "pacman"

    environment_data: dict[str, object] = {
        "environment_kind": environment.kind,
        "environment_root": environment.root,
        "environment_identity": environment.identity,
        "uname": environment.uname,
    }
    if environment.msystem:
        environment_data["msystem"] = environment.msystem

    observations = [
        DiscoveryObservation(
            "compatibility_environment",
            "windows_posix",
            ObservationAuthority.DIRECT,
            environment_data,
        )
    ]

    version = package_version
    if package_version is not None:
        observations.append(
            DiscoveryObservation(
                "manager_registration",
                manager,
                ObservationAuthority.DIRECT,
                {
                    "package": strategy.package_name,
                    "version": package_version,
                    "environment_identity": environment.identity,
                },
            )
        )

    if executable_in_environment and executable:
        observations.append(
            DiscoveryObservation(
                "executable_path",
                "windows_posix",
                ObservationAuthority.DIRECT,
                {
                    "executable": strategy.executable_name,
                    "path": executable,
                    "environment_identity": environment.identity,
                },
            )
        )
        if strategy.version_arguments:
            result = runner([executable, *strategy.version_arguments])
            if result.returncode == 0:
                raw = result.stdout.strip() or result.stderr.strip()
                if raw:
                    executable_version = raw.splitlines()[0].strip()
                    if version is None:
                        version = executable_version
                    observations.append(
                        DiscoveryObservation(
                            "version_probe",
                            strategy.executable_name,
                            ObservationAuthority.DIRECT,
                            {
                                "version_output": executable_version,
                                "environment_identity": environment.identity,
                            },
                        )
                    )

    if package_version is None and not executable_in_environment:
        errors = [value for value in (environment_error, package_error) if value]
        if executable and not executable_in_environment:
            errors.append(
                f"Resolved {strategy.executable_name!r} is outside the active compatibility environment root."
            )
        return [], "; ".join(errors) if errors else None

    identity_leaf = (
        strategy.package_name
        if package_version is not None
        else strategy.executable_name
    )
    return [
        InstallationCandidate(
            native_identity=f"{environment.identity}:{identity_leaf}",
            display_identity=strategy.package_name,
            version=version,
            paths=(executable,) if executable_in_environment and executable else (),
            scope=InstallationScope.UNKNOWN,
            registration_kind=(
                registration_kind if package_version is not None else "posix_executable"
            ),
            observations=tuple(observations),
        )
    ], package_error
