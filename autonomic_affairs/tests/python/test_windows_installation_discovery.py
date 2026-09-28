from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from annexation_procedures import windows_installation_discovery as windows_backend
from annexation_procedures.installation_discovery import discover_installation
from annexation_procedures.model import (
    BuiltInExecutableDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    InstallationPresence,
    InstallationScope,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
    TriState,
    WindowsAppxDiscovery,
    WindowsArpDiscovery,
    WingetPackageDiscovery,
)
from annexation_procedures.process import ProcessResult


class FakeWindowsDiscovery:
    def __init__(self) -> None:
        self.paths = {}
        self.winget_ids = set()
        self.versions = {}
        self.appx_payload = []

    def which(self, command: str) -> str | None:
        return self.paths.get(command)

    def run(self, argv: list[str]) -> ProcessResult:
        if argv[:2] == ["winget", "list"]:
            package_id = argv[argv.index("--id") + 1]
            return ProcessResult(
                0 if package_id in self.winget_ids else 1,
                "matched" if package_id in self.winget_ids else "",
                "",
            )

        executable = Path(argv[0]).name.lower()
        if executable == "powershell.exe" and "-Command" in argv and "Get-AppxPackage" in argv[-1]:
            return ProcessResult(0, json.dumps(self.appx_payload), "")
        if executable in self.versions:
            return ProcessResult(0, self.versions[executable] + "\n", "")
        raise AssertionError(f"Unexpected command: {argv!r}")


class WindowsInstallationDiscoveryTests(unittest.TestCase):
    def _context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True, root / "local"),
        )

    def test_arp_msi_exact_record_returns_structured_candidate(self) -> None:
        fake = FakeWindowsDiscovery()
        fake.paths["contour.exe"] = "C:/Program Files/Contour/contour.exe"
        record = windows_backend._ArpRecord(
            subkey="{11111111-2222-3333-4444-555555555555}",
            scope=InstallationScope.MACHINE,
            view="HKLM:64",
            display_name="Contour",
            display_version="0.6.1",
            publisher="Contour Terminal",
            install_location="C:/Program Files/Contour",
            install_source="C:/Temp",
            uninstall_string="msiexec /x {11111111-2222-3333-4444-555555555555}",
            windows_installer=True,
        )
        with patch.object(windows_backend, "_read_arp_records", return_value=([record], None)):
            candidates, error = windows_backend.arp_candidates(
                WindowsArpDiscovery(display_name="Contour", executable_name="contour.exe"),
                fake.which,
            )

        self.assertIsNone(error)
        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("arp_msi", candidate.registration_kind)
        self.assertEqual("0.6.1", candidate.version)
        self.assertEqual(InstallationScope.MACHINE, candidate.scope)
        self.assertEqual(("C:/Program Files/Contour/contour.exe",), candidate.paths)

    def test_appx_exact_family_returns_package_user_candidate(self) -> None:
        fake = FakeWindowsDiscovery()
        fake.paths["powershell.exe"] = "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
        fake.paths["pwsh.exe"] = "C:/Program Files/WindowsApps/Microsoft.PowerShell_7.6/pwsh.exe"
        fake.appx_payload = {
            "Name": "Microsoft.PowerShell",
            "PackageFullName": "Microsoft.PowerShell_7.6.0.0_x64__8wekyb3d8bbwe",
            "PackageFamilyName": "Microsoft.PowerShell_8wekyb3d8bbwe",
            "Version": "7.6.0.0",
            "InstallLocation": "C:/Program Files/WindowsApps/Microsoft.PowerShell_7.6",
            "PublisherId": "8wekyb3d8bbwe",
        }
        candidates, error = windows_backend.appx_candidates(
            WindowsAppxDiscovery("Microsoft.PowerShell_8wekyb3d8bbwe", executable_name="pwsh.exe"),
            fake.run,
            fake.which,
        )

        self.assertIsNone(error)
        self.assertEqual(1, len(candidates))
        self.assertEqual("msix_appx", candidates[0].registration_kind)
        self.assertEqual(InstallationScope.PACKAGE_USER, candidates[0].scope)
        self.assertEqual("7.6.0.0", candidates[0].version)
        self.assertIn(fake.paths["pwsh.exe"], candidates[0].paths)

    def test_winget_and_executable_merge(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWindowsDiscovery()
            fake.paths["winget"] = "C:/Users/fixture/AppData/Local/Microsoft/WindowsApps/winget.exe"
            fake.paths["oh-my-posh.exe"] = "C:/Program Files/oh-my-posh/bin/oh-my-posh.exe"
            fake.winget_ids.add("JanDeDobbeleer.OhMyPosh")
            fake.versions["oh-my-posh.exe"] = "27.0.0"
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan((
                    WingetPackageDiscovery(
                        "JanDeDobbeleer.OhMyPosh",
                        preferred=True,
                        executable_name="oh-my-posh.exe",
                        version_arguments=("version",),
                    ),
                    ExecutableDiscovery("oh-my-posh.exe", ("version",)),
                )),
            )
            assessment = discover_installation(
                "oh_my_posh", declaration, self._context(root),
                runner=fake.run, which=fake.which,
            )

        self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
        self.assertEqual(1, len(assessment.candidates))
        self.assertEqual("winget_correlation", assessment.candidates[0].registration_kind)
        self.assertEqual(TriState.YES, assessment.candidates[0].preferred_match)

    def test_unavailable_winget_does_not_hide_executable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWindowsDiscovery()
            fake.paths["example.exe"] = "C:/Tools/example.exe"
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan((
                    WingetPackageDiscovery("Vendor.Example"),
                    ExecutableDiscovery("example.exe"),
                )),
            )
            assessment = discover_installation(
                "example", declaration, self._context(root),
                runner=fake.run, which=fake.which,
            )

        self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
        self.assertEqual(1, len(assessment.candidates))
        self.assertIn("winget is unavailable.", assessment.errors)

    def test_powershell_side_by_side_remains_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWindowsDiscovery()
            fake.paths["powershell.exe"] = "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
            fake.paths["pwsh.exe"] = "C:/Program Files/WindowsApps/Microsoft.PowerShell_7.6/pwsh.exe"
            fake.versions["powershell.exe"] = "5.1.26100.1"
            fake.appx_payload = {
                "Name": "Microsoft.PowerShell",
                "PackageFullName": "Microsoft.PowerShell_7.6.0.0_x64__8wekyb3d8bbwe",
                "PackageFamilyName": "Microsoft.PowerShell_8wekyb3d8bbwe",
                "Version": "7.6.0.0",
                "InstallLocation": "C:/Program Files/WindowsApps/Microsoft.PowerShell_7.6",
                "PublisherId": "8wekyb3d8bbwe",
            }
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan((
                    WindowsAppxDiscovery("Microsoft.PowerShell_8wekyb3d8bbwe", executable_name="pwsh.exe"),
                    BuiltInExecutableDiscovery(
                        "powershell.exe",
                        "windows_powershell",
                        ("-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"),
                    ),
                )),
            )
            assessment = discover_installation(
                "powershell", declaration, self._context(root),
                runner=fake.run, which=fake.which,
            )

        self.assertEqual(InstallationPresence.AMBIGUOUS, assessment.presence)
        self.assertEqual({"msix_appx", "builtin"}, {c.registration_kind for c in assessment.candidates})


if __name__ == "__main__":
    unittest.main()
