"""Native Windows installation discovery backends."""

from __future__ import annotations

from dataclasses import dataclass
import json
import ntpath
import re
from typing import Callable

from .model import (
    BuiltInExecutableDiscovery,
    DiscoveryObservation,
    InstallationCandidate,
    InstallationScope,
    ObservationAuthority,
    TriState,
    WindowsAppxDiscovery,
    WindowsArpDiscovery,
)
from .process import ProcessResult


Runner = Callable[[list[str]], ProcessResult]
Which = Callable[[str], str | None]

_GUID = re.compile(r"^\{[0-9A-Fa-f-]{36}\}$")
_UNINSTALL_KEY = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"


@dataclass(frozen=True)
class _ArpRecord:
    subkey: str
    scope: InstallationScope
    view: str
    display_name: str | None
    display_version: str | None
    publisher: str | None
    install_location: str | None
    install_source: str | None
    uninstall_string: str | None
    windows_installer: bool

    @property
    def product_code(self) -> str | None:
        return self.subkey if _GUID.fullmatch(self.subkey) else None


def _read_arp_records() -> tuple[list[_ArpRecord], str | None]:
    try:
        import winreg
    except ImportError:
        return [], "winreg is unavailable."

    records: list[_ArpRecord] = []
    seen: set[tuple[str, str, str]] = set()
    hives = (
        ("HKCU", winreg.HKEY_CURRENT_USER, InstallationScope.USER),
        ("HKLM", winreg.HKEY_LOCAL_MACHINE, InstallationScope.MACHINE),
    )
    views = (
        ("default", 0),
        ("64", getattr(winreg, "KEY_WOW64_64KEY", 0)),
        ("32", getattr(winreg, "KEY_WOW64_32KEY", 0)),
    )

    for hive_name, hive, scope in hives:
        for view_name, view_flag in views:
            try:
                root = winreg.OpenKey(
                    hive,
                    _UNINSTALL_KEY,
                    0,
                    winreg.KEY_READ | view_flag,
                )
            except OSError:
                continue
            with root:
                index = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(root, index)
                    except OSError:
                        break
                    index += 1
                    try:
                        entry = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | view_flag)
                    except OSError:
                        continue
                    with entry:
                        def read(name: str) -> object | None:
                            try:
                                return winreg.QueryValueEx(entry, name)[0]
                            except OSError:
                                return None

                        display = read("DisplayName")
                        version = read("DisplayVersion")
                        publisher = read("Publisher")
                        install_location = read("InstallLocation")
                        install_source = read("InstallSource")
                        uninstall = read("QuietUninstallString") or read("UninstallString")
                        windows_installer = bool(read("WindowsInstaller"))

                    identity = (hive_name, view_name, subkey.casefold())
                    if identity in seen:
                        continue
                    seen.add(identity)
                    records.append(
                        _ArpRecord(
                            subkey=subkey,
                            scope=scope,
                            view=f"{hive_name}:{view_name}",
                            display_name=str(display) if display else None,
                            display_version=str(version) if version else None,
                            publisher=str(publisher) if publisher else None,
                            install_location=str(install_location) if install_location else None,
                            install_source=str(install_source) if install_source else None,
                            uninstall_string=str(uninstall) if uninstall else None,
                            windows_installer=windows_installer,
                        )
                    )
    return records, None


def _within(path: str, directory: str) -> bool:
    path_norm = ntpath.normcase(ntpath.normpath(path))
    dir_norm = ntpath.normcase(ntpath.normpath(directory))
    if not dir_norm:
        return False
    try:
        return ntpath.commonpath((path_norm, dir_norm)) == dir_norm
    except ValueError:
        return False


def arp_candidates(
    strategy: WindowsArpDiscovery,
    which: Which,
) -> tuple[list[InstallationCandidate], str | None]:
    records, error = _read_arp_records()
    if error is not None:
        return [], error

    executable = which(strategy.executable_name) if strategy.executable_name else None
    candidates: list[InstallationCandidate] = []

    for record in records:
        exact_identity = False
        if strategy.product_code is not None:
            if record.product_code is None or record.product_code.casefold() != strategy.product_code.casefold():
                continue
            exact_identity = True
        if strategy.display_name is not None:
            if record.display_name is None or record.display_name.casefold() != strategy.display_name.casefold():
                continue
            exact_identity = True
        if strategy.publisher is not None:
            if record.publisher is None or record.publisher.casefold() != strategy.publisher.casefold():
                continue

        executable_matches = bool(
            executable
            and record.install_location
            and _within(executable, record.install_location)
        )
        if not exact_identity and strategy.executable_name and not executable_matches:
            continue

        native_identity = (
            record.product_code
            or record.display_name
            or record.subkey
        )
        data: dict[str, object] = {
            "subkey": record.subkey,
            "view": record.view,
            "windows_installer": record.windows_installer,
        }
        for key, value in (
            ("display_name", record.display_name),
            ("version", record.display_version),
            ("publisher", record.publisher),
            ("install_location", record.install_location),
            ("install_source", record.install_source),
            ("uninstall_string", record.uninstall_string),
        ):
            if value:
                data[key] = value

        paths: tuple[str, ...] = ()
        observations = [
            DiscoveryObservation(
                "native_package_registration",
                "windows_arp",
                ObservationAuthority.DIRECT,
                data,
            )
        ]
        if executable_matches and executable:
            paths = (executable,)
            observations.append(
                DiscoveryObservation(
                    "executable_path",
                    "windows_arp",
                    ObservationAuthority.CORRELATED,
                    {"executable": strategy.executable_name, "path": executable},
                )
            )

        candidates.append(
            InstallationCandidate(
                native_identity=native_identity,
                display_identity=record.display_name,
                version=record.display_version,
                paths=paths,
                scope=record.scope,
                registration_kind="arp_msi" if record.windows_installer else "arp",
                preferred_match=TriState.YES if strategy.preferred else TriState.UNKNOWN,
                uninstall_identity=record.product_code or record.subkey,
                observations=tuple(observations),
            )
        )

    return candidates, None


def appx_candidates(
    strategy: WindowsAppxDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[list[InstallationCandidate], str | None]:
    powershell = which("powershell.exe")
    if powershell is None:
        return [], "powershell.exe is unavailable for AppX discovery."

    family = strategy.package_family_name.replace("'", "''")
    command = (
        "Get-AppxPackage | "
        f"Where-Object {{ $_.PackageFamilyName -eq '{family}' }} | "
        "Select-Object Name,PackageFullName,PackageFamilyName,@{Name='Version';Expression={$_.Version.ToString()}},InstallLocation,PublisherId | "
        "ConvertTo-Json -Compress"
    )
    result = runner([powershell, "-NoProfile", "-Command", command])
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        return [], f"AppX discovery failed: {detail}"

    raw = result.stdout.strip()
    if not raw:
        return [], None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [], f"AppX discovery returned invalid JSON: {exc}"

    items = payload if isinstance(payload, list) else [payload]
    candidates: list[InstallationCandidate] = []
    resolved_executable = which(strategy.executable_name) if strategy.executable_name else None

    for item in items:
        if not isinstance(item, dict):
            continue
        package_family = str(item.get("PackageFamilyName") or "")
        if package_family.casefold() != strategy.package_family_name.casefold():
            continue

        install_location = str(item.get("InstallLocation") or "")
        executable_matches = bool(
            resolved_executable
            and install_location
            and _within(resolved_executable, install_location)
        )
        paths = tuple(
            value
            for value in (
                install_location or None,
                resolved_executable if executable_matches else None,
            )
            if value
        )
        data = {
            key: value
            for key, value in {
                "name": item.get("Name"),
                "package_full_name": item.get("PackageFullName"),
                "package_family_name": item.get("PackageFamilyName"),
                "version": item.get("Version"),
                "install_location": item.get("InstallLocation"),
                "publisher_id": item.get("PublisherId"),
            }.items()
            if value not in (None, "")
        }
        observations = [
            DiscoveryObservation(
                "native_package_registration",
                "appx",
                ObservationAuthority.DIRECT,
                data,
            )
        ]
        if executable_matches and resolved_executable:
            observations.append(
                DiscoveryObservation(
                    "executable_path",
                    "appx",
                    ObservationAuthority.CORRELATED,
                    {
                        "executable": strategy.executable_name,
                        "path": resolved_executable,
                    },
                )
            )
        candidates.append(
            InstallationCandidate(
                native_identity=strategy.package_family_name,
                display_identity=str(item.get("Name") or "") or None,
                version=str(item.get("Version") or "") or None,
                paths=paths,
                scope=InstallationScope.PACKAGE_USER,
                registration_kind="msix_appx",
                preferred_match=TriState.YES if strategy.preferred else TriState.UNKNOWN,
                uninstall_identity=str(item.get("PackageFullName") or "") or None,
                observations=tuple(observations),
            )
        )

    return candidates, None


def builtin_candidate(
    strategy: BuiltInExecutableDiscovery,
    runner: Runner,
    which: Which,
) -> tuple[InstallationCandidate | None, str | None]:
    path = which(strategy.executable_name)
    if path is None:
        return None, None

    version = None
    observations = [
        DiscoveryObservation(
            "platform_capability",
            "windows",
            ObservationAuthority.DIRECT,
            {
                "identity": strategy.identity,
                "executable": strategy.executable_name,
                "path": path,
            },
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

    return (
        InstallationCandidate(
            native_identity=strategy.identity,
            version=version,
            paths=(path,),
            scope=InstallationScope.MACHINE,
            registration_kind="builtin",
            observations=tuple(observations),
        ),
        None,
    )
