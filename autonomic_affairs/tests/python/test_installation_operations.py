from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    Application,
    AptPackage,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
    WingetPackage,
)
from annexation_procedures.operations.installation import (
    check_installed,
    install_application,
    uninstall_application,
)
from annexation_procedures.process import ProcessResult
from annexation_procedures.state import read_install_state


class FakeApt:
    def __init__(self, installed: bool = False) -> None:
        self.installed = installed
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        command = argv[0]
        if command == "dpkg-query":
            return ProcessResult(
                0 if self.installed else 1,
                "Status: install ok installed\n" if self.installed else "",
                "",
            )
        if command == "apt-get":
            if "install" in argv:
                self.installed = True
            elif "remove" in argv:
                self.installed = False
            return ProcessResult(0, "", "")
        raise AssertionError(f"Unexpected apt command: {argv!r}")


class FakeWinget:
    def __init__(self, installed: bool = False) -> None:
        self.installed = installed
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        if argv[:2] == ["winget", "list"]:
            return ProcessResult(0 if self.installed else 1, "", "")
        if argv[:2] == ["winget", "install"]:
            self.installed = True
            return ProcessResult(0, "", "")
        if argv[:2] == ["winget", "uninstall"]:
            self.installed = False
            return ProcessResult(0, "", "")
        raise AssertionError(f"Unexpected WinGet command: {argv!r}")


class InstallationOperationTests(unittest.TestCase):
    def _context(self, root: Path, platform: Platform, *, dry_run: bool = False) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=platform,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True),
            dry_run=dry_run,
        )

    def test_apt_install_and_uninstall_record_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt()
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
            which = lambda command: f"/usr/bin/{command}"

            installed = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=which,
                geteuid=lambda: 0,
            )
            self.assertEqual("installed_managed", installed.code)
            self.assertTrue(installed.changed)
            self.assertIsNotNone(read_install_state(context, "fish"))
            self.assertEqual("installed_managed", check_installed(app, declaration, context, runner=fake).code)

            removed = uninstall_application(
                app,
                declaration,
                context,
                runner=fake,
                which=which,
                geteuid=lambda: 0,
            )
            self.assertEqual("not_installed", removed.code)
            self.assertTrue(removed.changed)
            self.assertIsNone(read_install_state(context, "fish"))

    def test_unmanaged_install_is_never_claimed_or_removed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt(installed=True)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
            which = lambda command: f"/usr/bin/{command}"

            install_result = install_application(
                app, declaration, context, runner=fake, which=which, geteuid=lambda: 0
            )
            self.assertEqual("installed_unmanaged", install_result.code)
            self.assertIsNone(read_install_state(context, "fish"))

            uninstall_result = uninstall_application(
                app, declaration, context, runner=fake, which=which, geteuid=lambda: 0
            )
            self.assertEqual("installed_unmanaged", uninstall_result.code)
            self.assertTrue(fake.installed)

    def test_dry_run_does_not_install_or_record_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt()
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX, dry_run=True)

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )
            self.assertEqual("would_install", result.code)
            self.assertFalse(result.changed)
            self.assertFalse(fake.installed)
            self.assertIsNone(read_install_state(context, "fish"))

    def test_winget_strategy_uses_shared_handler(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWinget()
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                install_strategy=WingetPackage("Vendor.Example"),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = self._context(root, Platform.WINDOWS)

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: "winget.exe" if command == "winget" else None,
            )
            self.assertEqual("installed_managed", result.code)
            self.assertTrue(fake.installed)

            result = uninstall_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: "winget.exe" if command == "winget" else None,
            )
            self.assertEqual("not_installed", result.code)
            self.assertFalse(fake.installed)


if __name__ == "__main__":
    unittest.main()
