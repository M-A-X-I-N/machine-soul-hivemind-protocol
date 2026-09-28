from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    Application,
    AptPackage,
    DpkgPackageDiscovery,
    ExecutableDiscovery,
    InstallationDiscoveryPlan,
    InstallationScope,
    InstallationScopePolicy,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
    WingetPackage,
    WingetPackageDiscovery,
)
from annexation_procedures.operations.installation import (
    check_installed,
    install_application,
    uninstall_application,
)
from annexation_procedures.process import ProcessResult
from annexation_procedures.state import (
    InstallState,
    read_install_state,
    read_install_states,
    write_install_state,
)


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
    def __init__(self, installed: bool = False, *, scopes: set[str] | None = None) -> None:
        self.installed_scopes = set(scopes or ())
        if installed:
            self.installed_scopes.add("user")
        self.calls: list[list[str]] = []

    @property
    def installed(self) -> bool:
        return bool(self.installed_scopes)

    def __call__(self, argv: list[str]) -> ProcessResult:
        self.calls.append(list(argv))
        scope = argv[argv.index("--scope") + 1] if "--scope" in argv else None
        if argv[:2] == ["winget", "list"]:
            return ProcessResult(0 if scope in self.installed_scopes else 1, "", "")
        if argv[:2] == ["winget", "install"]:
            assert scope is not None
            self.installed_scopes.add(scope)
            return ProcessResult(0, "", "")
        if argv[:2] == ["winget", "uninstall"]:
            assert scope is not None
            self.installed_scopes.discard(scope)
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
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
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
            self.assertEqual(
                "installed_managed",
                check_installed(
                    app,
                    declaration,
                    context,
                    runner=fake,
                    which=lambda command: f"/usr/bin/{command}",
                ).code,
            )

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
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
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

    def test_legacy_provenance_blocks_install_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt()
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
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

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )

            self.assertEqual("installation_provenance_unreconciled", result.code)
            self.assertFalse(any("apt-get" in call for call in fake.calls))

    def test_uninstall_clears_exact_stale_scoped_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt(installed=False)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
            write_install_state(
                context,
                InstallState(
                    application="fish",
                    host=context.host,
                    account=context.target_account.name,
                    manager="apt",
                    identity="fish",
                    requested_scope_mode=declaration.install_strategy.scope_policy.mode,
                    requested_scope=InstallationScope.MACHINE,
                    actual_scope=InstallationScope.MACHINE,
                    native_identity="fish",
                ),
            )

            result = uninstall_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )

            self.assertEqual("not_installed", result.code)
            self.assertTrue(result.changed)
            self.assertEqual((), read_install_states(context, "fish"))

    def test_apt_machine_ownership_is_shared_across_target_accounts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt()
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            first = self._context(root, Platform.LINUX)

            installed = install_application(
                app,
                declaration,
                first,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )
            self.assertEqual("installed_managed", installed.code)

            second = OperationContext(
                repository_root=root,
                platform=Platform.LINUX,
                host=first.host,
                target_account=TargetAccount("second_user", root / "second-home", True),
            )
            checked = check_installed(
                app,
                declaration,
                second,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
            )
            self.assertEqual("installed_managed", checked.code)
            self.assertEqual(1, len(read_install_states(second, "fish")))
            self.assertEqual(
                InstallationScope.MACHINE,
                read_install_states(second, "fish")[0].actual_scope,
            )

    def test_apt_single_legacy_record_reconciles_without_reinstall(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt(installed=True)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
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

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )

            self.assertEqual("installed_managed", result.code)
            self.assertFalse(any(call and call[0] == "apt-get" for call in fake.calls))
            state = read_install_state(context, "fish")
            self.assertIsNotNone(state)
            assert state is not None
            self.assertEqual(InstallationScope.MACHINE, state.actual_scope)

    def test_apt_duplicate_legacy_records_refuse_reconciliation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt(installed=True)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
            )
            app = Application(id="fish", display_name="Fish", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
            for account in ("fixture_user", "other_user"):
                write_install_state(
                    context,
                    InstallState(
                        application="fish",
                        host=context.host,
                        account=account,
                        manager="apt",
                        identity="fish",
                    ),
                )

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: f"/usr/bin/{command}",
                geteuid=lambda: 0,
            )

            self.assertEqual("installation_provenance_ambiguous", result.code)
            self.assertFalse(any(call and call[0] == "apt-get" for call in fake.calls))

    def test_check_installed_can_work_without_install_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan(
                    (ExecutableDiscovery("example"),)
                ),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)

            result = check_installed(
                app,
                declaration,
                context,
                which=lambda command: "/opt/example/bin/example" if command == "example" else None,
            )

            self.assertEqual("installed_unmanaged", result.code)
            self.assertEqual("present", result.data["assessment"]["presence"])
            self.assertEqual(
                "/opt/example/bin/example",
                result.data["assessment"]["candidates"][0]["paths"][0],
            )

    def test_check_installed_reports_unknown_when_backend_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("example"),)
                ),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)

            result = check_installed(
                app,
                declaration,
                context,
                runner=lambda argv: (_ for _ in ()).throw(AssertionError("runner should not run")),
                which=lambda command: None,
            )

            self.assertEqual("installation_unknown", result.code)
            self.assertEqual("unknown", result.data["assessment"]["presence"])

    def test_check_installed_retains_multiple_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                installation_discovery=InstallationDiscoveryPlan(
                    (
                        ExecutableDiscovery("example"),
                        ExecutableDiscovery("example-alt"),
                    )
                ),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = self._context(root, Platform.LINUX)
            paths = {
                "example": "/usr/bin/example",
                "example-alt": "/opt/example/bin/example",
            }

            result = check_installed(
                app,
                declaration,
                context,
                which=lambda command: paths.get(command),
            )

            self.assertEqual("installed_ambiguous", result.code)
            self.assertEqual("ambiguous", result.data["assessment"]["presence"])
            self.assertEqual(2, len(result.data["assessment"]["candidates"]))

    def test_dry_run_does_not_install_or_record_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeApt()
            declaration = PlatformDeclaration(
                platform=Platform.LINUX,
                capabilities={},
                install_strategy=AptPackage("fish"),
                installation_discovery=InstallationDiscoveryPlan(
                    (DpkgPackageDiscovery("fish", preferred=True),)
                ),
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

    def test_winget_other_scope_does_not_block_exact_owned_scope(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWinget(scopes={"machine"})
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                install_strategy=WingetPackage(
                    "Vendor.Example",
                    InstallationScopePolicy.required(InstallationScope.USER),
                ),
                installation_discovery=InstallationDiscoveryPlan(
                    (WingetPackageDiscovery("Vendor.Example", preferred=True),)
                ),
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
            self.assertEqual({"user", "machine"}, fake.installed_scopes)

            removed = uninstall_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: "winget.exe" if command == "winget" else None,
            )
            self.assertEqual("not_installed", removed.code)
            self.assertEqual({"machine"}, fake.installed_scopes)

    def test_noncurrent_user_scope_is_refused_before_winget_runs(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWinget()
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                install_strategy=WingetPackage(
                    "Vendor.Example",
                    InstallationScopePolicy.required(InstallationScope.USER),
                ),
                installation_discovery=InstallationDiscoveryPlan(
                    (WingetPackageDiscovery("Vendor.Example", preferred=True),)
                ),
            )
            app = Application(id="example", display_name="Example", platforms=(declaration,))
            context = OperationContext(
                repository_root=root,
                platform=Platform.WINDOWS,
                host="fixture_host",
                target_account=TargetAccount("other_user", root / "other", False),
            )

            result = install_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: "winget.exe" if command == "winget" else None,
            )

            self.assertEqual("installation_scope_target_unsupported", result.code)
            self.assertEqual([], fake.calls)

    def test_winget_user_scope_is_explicit_and_owned(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = FakeWinget()
            declaration = PlatformDeclaration(
                platform=Platform.WINDOWS,
                capabilities={},
                install_strategy=WingetPackage(
                    "Vendor.Example",
                    InstallationScopePolicy.required(InstallationScope.USER),
                ),
                installation_discovery=InstallationDiscoveryPlan(
                    (WingetPackageDiscovery("Vendor.Example", preferred=True),)
                ),
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
            self.assertEqual({"user"}, fake.installed_scopes)
            state = read_install_state(context, "example")
            self.assertIsNotNone(state)
            assert state is not None
            self.assertEqual(InstallationScope.USER, state.actual_scope)

            install_call = next(call for call in fake.calls if call[:2] == ["winget", "install"])
            self.assertEqual("user", install_call[install_call.index("--scope") + 1])

            removed = uninstall_application(
                app,
                declaration,
                context,
                runner=fake,
                which=lambda command: "winget.exe" if command == "winget" else None,
            )
            self.assertEqual("not_installed", removed.code)
            self.assertEqual(set(), fake.installed_scopes)
            uninstall_call = next(call for call in fake.calls if call[:2] == ["winget", "uninstall"])
            self.assertEqual("user", uninstall_call[uninstall_call.index("--scope") + 1])


if __name__ == "__main__":
    unittest.main()
