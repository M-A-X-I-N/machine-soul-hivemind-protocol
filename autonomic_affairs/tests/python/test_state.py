from __future__ import annotations

import base64
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.model import (
    InstallationScope,
    InstallationScopePolicyMode,
    OperationContext,
    Platform,
    TargetAccount,
)
from annexation_procedures.state import (
    ConfigState,
    InstallState,
    config_state_path,
    delete_config_state,
    delete_scoped_install_state,
    install_state_path,
    read_config_state,
    read_install_state,
    read_install_states,
    read_legacy_install_state,
    read_legacy_install_states,
    reconcile_legacy_install_state,
    resolve_backup_path,
    scoped_install_state_path,
    write_config_state,
    write_install_state,
)


def b64(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


class StateTests(unittest.TestCase):
    def _context(self, root: Path) -> OperationContext:
        return OperationContext(
            repository_root=root,
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", root / "home", True),
        )

    def test_round_trip_new_config_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = root / "native/config"
            state = ConfigState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                source_relative="assimilation_directives/example/default/common/config",
                destination=str(destination),
                prior_type="file",
                backup_relative="scratch/backups/example/original",
                backup_absolute=None,
                prior_target=None,
                applied_target=str(root / "source"),
                applied_utc="2026-01-01T00:00:00Z",
            )
            write_config_state(context, state)
            loaded = read_config_state(context, "example", destination)
            self.assertEqual(state, loaded)
            self.assertEqual(root / "scratch/backups/example/original", resolve_backup_path(context, loaded))

    def test_reads_legacy_linux_line_state(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = root / "native/config"
            path = config_state_path(context, "example", destination, extension=".state")
            path.parent.mkdir(parents=True)
            path.write_text(
                "\n".join(
                    [
                        "schema=2",
                        f"application_b64={b64('example')}",
                        f"host_b64={b64(context.host)}",
                        f"account_b64={b64(context.target_account.name)}",
                        f"source_relative_b64={b64('assimilation_directives/example/default/common/config')}",
                        f"destination_b64={b64(str(destination))}",
                        "prior_type=absent",
                        f"backup_relative_b64={b64('')}",
                        f"backup_b64={b64('')}",
                        f"prior_target_b64={b64('')}",
                        f"applied_target_b64={b64(str(root / 'old/source'))}",
                        "applied_utc=2026-01-01T00:00:00Z",
                    ]
                ) + "\n",
                encoding="utf-8",
            )
            loaded = read_config_state(context, "example", destination)
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual("example", loaded.application)
            self.assertEqual(str(root / "old/source"), loaded.applied_target)

    def test_round_trip_install_state_and_read_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            current = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="example-package",
                metadata={"source": "fixture"},
            )
            write_install_state(context, current)
            self.assertEqual(current, read_install_state(context, "example"))

            install_state_path(context, "example").unlink()
            legacy = install_state_path(context, "example", extension=".state")
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_text(
                "schema=1\napplication=example\nmanager=apt\npackage=example-package\n"
                f"host={context.host}\naccount={context.target_account.name}\n",
                encoding="utf-8",
            )
            loaded = read_install_state(context, "example")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual("example-package", loaded.identity)

    def test_scoped_install_state_keeps_user_and_machine_records_separate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            user = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="winget",
                identity="Vendor.Example",
                requested_scope_mode=InstallationScopePolicyMode.REQUIRED,
                requested_scope=InstallationScope.USER,
                actual_scope=InstallationScope.USER,
                scope_subject=context.target_account.name,
                native_identity="Vendor.Example",
                uninstall_identity="Vendor.Example",
            )
            machine = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="winget",
                identity="Vendor.Example",
                requested_scope_mode=InstallationScopePolicyMode.REQUIRED,
                requested_scope=InstallationScope.MACHINE,
                actual_scope=InstallationScope.MACHINE,
                native_identity="Vendor.Example",
                uninstall_identity="Vendor.Example",
            )

            user_path = write_install_state(context, user)
            machine_path = write_install_state(context, machine)

            self.assertIn("user", user_path.parts)
            self.assertIn(context.target_account.name, user_path.parts)
            self.assertIn("machine", machine_path.parts)
            self.assertNotEqual(user_path, machine_path)
            self.assertEqual({user, machine}, set(read_install_states(context, "example")))

            delete_scoped_install_state(context, user)
            self.assertEqual((machine,), read_install_states(context, "example"))
            self.assertTrue(machine_path.is_file())

    def test_scoped_install_state_requires_valid_subject(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            with self.assertRaises(ValueError):
                scoped_install_state_path(
                    context,
                    "example",
                    manager="winget",
                    identity="Vendor.Example",
                    actual_scope=InstallationScope.USER,
                )
            with self.assertRaises(ValueError):
                InstallState(
                    application="example",
                    host=context.host,
                    account=context.target_account.name,
                    manager="winget",
                    identity="Vendor.Example",
                    actual_scope=InstallationScope.MACHINE,
                    scope_subject=context.target_account.name,
                )

    def test_legacy_install_state_is_scope_unknown_and_enumerable(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            legacy = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="example-package",
            )
            path = write_install_state(context, legacy)
            self.assertEqual(install_state_path(context, "example"), path)

            loaded = read_legacy_install_state(context, "example")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(InstallationScope.UNKNOWN, loaded.actual_scope)
            self.assertEqual((loaded,), read_legacy_install_states(context, "example"))

    def test_reconcile_legacy_install_state_is_explicit_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            legacy = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="example-package",
            )
            write_install_state(context, legacy)
            loaded = read_legacy_install_state(context, "example")
            assert loaded is not None

            replacement = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="example-package",
                requested_scope_mode=InstallationScopePolicyMode.FIXED,
                requested_scope=InstallationScope.MACHINE,
                actual_scope=InstallationScope.MACHINE,
                native_identity="example-package",
                uninstall_identity="example-package",
            )
            path = reconcile_legacy_install_state(context, loaded, replacement)

            self.assertTrue(path.is_file())
            self.assertIsNone(read_legacy_install_state(context, "example"))
            self.assertEqual((replacement,), read_install_states(context, "example"))

    def test_reconcile_legacy_install_state_refuses_identity_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            legacy = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="example-package",
            )
            replacement = InstallState(
                application="example",
                host=context.host,
                account=context.target_account.name,
                manager="apt",
                identity="different-package",
                requested_scope_mode=InstallationScopePolicyMode.FIXED,
                requested_scope=InstallationScope.MACHINE,
                actual_scope=InstallationScope.MACHINE,
            )

            with self.assertRaisesRegex(Exception, "identity mismatch"):
                reconcile_legacy_install_state(context, legacy, replacement)

    def test_delete_config_state_removes_new_and_legacy_names(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = self._context(root)
            destination = root / "dest"
            for extension in (".json", ".state"):
                path = config_state_path(context, "example", destination, extension=extension)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding="utf-8")
            delete_config_state(context, "example", destination)
            self.assertFalse(config_state_path(context, "example", destination).exists())
            self.assertFalse(config_state_path(context, "example", destination, extension=".state").exists())


if __name__ == "__main__":
    unittest.main()
