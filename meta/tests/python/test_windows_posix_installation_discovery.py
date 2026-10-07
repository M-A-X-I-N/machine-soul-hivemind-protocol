from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation.installation_discovery import discover_installation
from annexation.model import (
    InstallationDiscoveryPlan,
    InstallationPresence,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
    WindowsPosixPackageDiscovery,
)
from annexation.process import ProcessResult
from annexation.windows_posix_installation_discovery import (
    discover_windows_posix_environment,
)


class FakePosixEnvironment:
    def __init__(
        self,
        *,
        uname: str,
        root: str,
        paths: dict[str, str],
        packages: dict[str, str] | None = None,
    ) -> None:
        self.uname = uname
        self.root = root
        self.paths = dict(paths)
        self.packages = packages or {}

    def which(self, command: str) -> str | None:
        return self.paths.get(command)

    def run(self, argv: list[str]) -> ProcessResult:
        command = Path(argv[0]).name.lower()
        if command in {"uname", "uname.exe"} and argv[1:] == ["-s"]:
            return ProcessResult(0, self.uname + "\n", "")
        if command in {"cygpath", "cygpath.exe"} and argv[1:] == ["-w", "/"]:
            return ProcessResult(0, self.root + "\n", "")
        if command in {"pacman", "pacman.exe"} and argv[1:2] == ["-Q"]:
            package = argv[2]
            version = self.packages.get(package)
            return ProcessResult(
                0 if version else 1,
                f"{package} {version}\n" if version else "",
                "",
            )
        if command in {"cygcheck", "cygcheck.exe"} and argv[1:3] == ["-c", "-d"]:
            package = argv[3]
            version = self.packages.get(package)
            output = (
                "Cygwin Package Information\n"
                "Package Version Status\n"
                f"{package} {version} OK\n"
                if version
                else "Cygwin Package Information\nPackage Version Status\n"
            )
            return ProcessResult(0, output, "")
        if command.rstrip(".exe") in {"bash", "zsh", "fish"} and "--version" in argv:
            return ProcessResult(0, f"{command} version fixture\n", "")
        raise AssertionError(f"Unexpected command: {argv!r}")


class WindowsPosixInstallationDiscoveryTests(unittest.TestCase):
    def _context(self, root: Path, *, msystem: str | None = None) -> OperationContext:
        environment = {"PATH": "fixture"}
        if msystem:
            environment["MSYSTEM"] = msystem
        return OperationContext(
            repository_root=root,
            platform=Platform.WINDOWS,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True, root / "local"),
            environment=environment,
        )

    def _declaration(self, app: str) -> PlatformDeclaration:
        return PlatformDeclaration(
            platform=Platform.WINDOWS,
            capabilities={},
            installation_discovery=InstallationDiscoveryPlan(
                (WindowsPosixPackageDiscovery(app, app, ("--version",)),)
            ),
        )

    def test_msys2_package_and_executable_share_environment_identity(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakePosixEnvironment(
                uname="MINGW64_NT-10.0-26100",
                root="C:/msys64",
                paths={
                    "cygpath": "C:/msys64/usr/bin/cygpath.exe",
                    "uname": "C:/msys64/usr/bin/uname.exe",
                    "pacman": "C:/msys64/usr/bin/pacman.exe",
                    "fish": "C:/msys64/usr/bin/fish.exe",
                },
                packages={"fish": "4.0.2-1"},
            )
            assessment = discover_installation(
                "fish",
                self._declaration("fish"),
                self._context(root, msystem="MINGW64"),
                runner=fake.run,
                which=fake.which,
            )

        self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
        candidate = assessment.candidates[0]
        self.assertEqual("msys2_package", candidate.registration_kind)
        self.assertEqual("4.0.2-1", candidate.version)
        environment = next(o for o in candidate.observations if o.kind == "compatibility_environment")
        self.assertEqual("msys2_style", environment.data["environment_kind"])
        self.assertIn("c:\\msys64", candidate.native_identity.casefold())

    def test_cygwin_uses_cygcheck_package_database(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakePosixEnvironment(
                uname="CYGWIN_NT-10.0-26100",
                root="C:/cygwin64",
                paths={
                    "cygpath": "C:/cygwin64/bin/cygpath.exe",
                    "uname": "C:/cygwin64/bin/uname.exe",
                    "cygcheck": "C:/cygwin64/bin/cygcheck.exe",
                    "zsh": "C:/cygwin64/bin/zsh.exe",
                },
                packages={"zsh": "5.9-1"},
            )
            assessment = discover_installation(
                "zsh",
                self._declaration("zsh"),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

        self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
        self.assertEqual("cygwin_package", assessment.candidates[0].registration_kind)
        self.assertEqual("5.9-1", assessment.candidates[0].version)

    def test_missing_package_manager_keeps_in_environment_executable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakePosixEnvironment(
                uname="MINGW64_NT-10.0-26100",
                root="C:/Program Files/Git",
                paths={
                    "cygpath": "C:/Program Files/Git/usr/bin/cygpath.exe",
                    "uname": "C:/Program Files/Git/usr/bin/uname.exe",
                    "bash": "C:/Program Files/Git/usr/bin/bash.exe",
                },
            )
            assessment = discover_installation(
                "bash",
                self._declaration("bash"),
                self._context(root, msystem="MINGW64"),
                runner=fake.run,
                which=fake.which,
            )

        self.assertEqual(InstallationPresence.PRESENT, assessment.presence)
        self.assertEqual("posix_executable", assessment.candidates[0].registration_kind)
        self.assertIn("pacman is unavailable", assessment.errors[0])

    def test_missing_environment_tooling_is_unknown_not_absent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakePosixEnvironment(uname="", root="", paths={})
            assessment = discover_installation(
                "fish",
                self._declaration("fish"),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

        self.assertEqual(InstallationPresence.UNKNOWN, assessment.presence)
        self.assertEqual(0, len(assessment.candidates))

    def test_executable_outside_active_root_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakePosixEnvironment(
                uname="MINGW64_NT-10.0-26100",
                root="C:/msys64",
                paths={
                    "cygpath": "C:/msys64/usr/bin/cygpath.exe",
                    "uname": "C:/msys64/usr/bin/uname.exe",
                    "fish": "C:/Tools/fish.exe",
                },
            )
            assessment = discover_installation(
                "fish",
                self._declaration("fish"),
                self._context(root),
                runner=fake.run,
                which=fake.which,
            )

        self.assertEqual(InstallationPresence.UNKNOWN, assessment.presence)
        self.assertEqual(0, len(assessment.candidates))
        self.assertIn("outside the active compatibility environment root", assessment.errors[0])

    def test_environment_identity_includes_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            one = FakePosixEnvironment(
                uname="MINGW64_NT-10.0",
                root="C:/msys64",
                paths={
                    "cygpath": "C:/msys64/usr/bin/cygpath.exe",
                    "uname": "C:/msys64/usr/bin/uname.exe",
                },
            )
            two = FakePosixEnvironment(
                uname="MINGW64_NT-10.0",
                root="D:/portable-msys",
                paths={
                    "cygpath": "D:/portable-msys/usr/bin/cygpath.exe",
                    "uname": "D:/portable-msys/usr/bin/uname.exe",
                },
            )
            env_one, _ = discover_windows_posix_environment(self._context(root), one.run, one.which)
            env_two, _ = discover_windows_posix_environment(self._context(root), two.run, two.which)

        assert env_one and env_two
        self.assertNotEqual(env_one.identity, env_two.identity)


if __name__ == "__main__":
    unittest.main()
