from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation_procedures.installation_discovery import discover_installation
from annexation_procedures.model import (
    Application,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    InstallationOwnership,
    InstallationPresence,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
    TriState,
)
from annexation_procedures.operations.installation import check_installed
from annexation_procedures.process import ProcessResult
from annexation_procedures.state import InstallState, write_install_state


class FakeLinuxDiscovery:
    def __init__(
        self,
        *,
        packages: dict[str, tuple[str, str]] | None = None,
        executables: dict[str, str] | None = None,
        owners: dict[str, str] | None = None,
        versions: dict[str, str] | None = None,
        dpkg_available: bool = True,
    ) -> None:
        self.packages = packages or {}
        self.executables = executables or {}
        self.owners = owners or {}
        self.versions = versions or {}
        self.dpkg_available = dpkg_available
        self.calls: list[list[str]] = []

    def which(self, command: str) -> str | None:
        if command == "dpkg-query":
            return "/usr/bin/dpkg-query" if self.dpkg_available else None
        return self.executables.get(command)

    def run(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        if argv[:2] == ["dpkg-query", "-W"]:
            package = argv[-1]
            entry = self.packages.get(package)
            if entry is None:
                return ProcessResult(1, "", "")
            version, architecture = entry
            return ProcessResult(
                0,
                f"{package}\t{version}\t{architecture}\tinstall ok installed",
                "",
            )

        if argv[:2] == ["dpkg-query", "-S"]:
            path = argv[-1]
            owner = self.owners.get(path)
            if owner is None:
                return ProcessResult(1, "", "")
            return ProcessResult(0, f"{owner}: {path}\n", "")

        executable = Path(argv[0]).name
        if executable in self.versions:
            return ProcessResult(0, self.versions[executable] + "\n", "")
        raise AssertionError(f"Unexpected command: {argv!r}")


class LinuxInstallationDiscoveryTests(unittest.TestCase):
    def _context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True),
        )

    def _declaration(self) -> PlatformDeclaration:
        return PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={},
            installation_discovery=InstallationDiscoveryPlan(
                (
                    DpkgPackageDiscovery(
                        "fish",
                        executable_name="fish",
                        preferred=True,
                    ),
                    ExecutableDiscovery("fish", ("--version",)),
                )
            ),
        )

    def test_dpkg_and_executable_evidence_merge_into_one_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeLinuxDiscovery(
                packages={"fish": ("4.9.3-1", "amd64")},
                executables={"fish": "/usr/bin/fish"},
                owners={"/usr/bin/fish": "fish"},
                versions={"fish": "fish, version 4.9.3"},
            )

            assessment = discover_installation(
                "fish",
                self._declaration(),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

            self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
            self.assertEqual(1, len(assessment.candidates))
            candidate = assessment.candidates[0]
            self.assertEqual("fish", candidate.native_identity)
            self.assertEqual("dpkg", candidate.registration_kind)
            self.assertEqual("4.9.3-1", candidate.version)
            self.assertEqual(("/usr/bin/fish",), candidate.paths)
            self.assertEqual(TriState.YES, candidate.preferred_match)
            self.assertEqual(TriState.YES, candidate.manageable_by_preferred_strategy)
            kinds = {item.kind for item in candidate.observations}
            self.assertIn("manager_registration", kinds)
            self.assertIn("file_owner", kinds)
            self.assertIn("executable_path", kinds)

    def test_manual_executable_remains_foreign_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeLinuxDiscovery(
                executables={"fish": "/usr/local/bin/fish"},
                versions={"fish": "fish, version 4.9.3"},
            )
            result = check_installed(
                Application(
                    id="fish",
                    display_name="Fish",
                    platforms=(self._declaration(),),
                ),
                self._declaration(),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

            self.assertEqual("installed_unmanaged", result.code)
            assessment = result.data["assessment"]
            self.assertEqual("present", assessment["presence"])
            self.assertEqual("executable", assessment["candidates"][0]["registration_kind"])
            self.assertEqual("unknown", assessment["candidates"][0]["preferred_match"])

    def test_optional_dpkg_backend_failure_does_not_hide_executable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeLinuxDiscovery(
                executables={"fish": "/opt/fish/bin/fish"},
                versions={"fish": "fish, version 4.9.3"},
                dpkg_available=False,
            )
            assessment = discover_installation(
                "fish",
                self._declaration(),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

            self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
            self.assertEqual(1, len(assessment.candidates))
            self.assertIn("dpkg-query is unavailable.", assessment.errors)

    def test_stale_provenance_is_distinct_from_absence(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            write_install_state(
                context,
                InstallState(
                    application="fish",
                    host=context.host,
                    account=context.target_account.name,
                    manager="apt",
                    identity="fish",
                ),
            )
            fake = FakeLinuxDiscovery()

            assessment = discover_installation(
                "fish",
                self._declaration(),
                context,
                runner=fake.run,
                which=fake.which,
            )

            self.assertEqual(InstallationPresence.ABSENT, assessment.presence)
            self.assertEqual(InstallationOwnership.STALE, assessment.machine_soul_state)

    def test_package_and_unowned_path_remain_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeLinuxDiscovery(
                packages={"fish": ("4.9.3-1", "amd64")},
                executables={"fish": "/usr/local/bin/fish"},
                versions={"fish": "fish, version 4.9.3"},
            )

            assessment = discover_installation(
                "fish",
                self._declaration(),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

            self.assertEqual(InstallationPresence.AMBIGUOUS, assessment.presence)
            self.assertEqual(2, len(assessment.candidates))


if __name__ == "__main__":
    unittest.main()
