from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest

from annexation_procedures.model import (
    Application,
    ConfigurationFile,
    ConflictPolicy,
    HomeRelativeDestination,
    OperationContext,
    Platform,
    PlatformDeclaration,
    TargetAccount,
)
from annexation_procedures.operations import apply_config, check_config, unapply_config


class ConfigurationOperationTests(unittest.TestCase):
    def _build(
        self,
        root: Path,
        *,
        configs: tuple[ConfigurationFile, ...] | None = None,
        home: Path | None = None,
    ) -> tuple[Application, PlatformDeclaration, OperationContext]:
        (root / ".machine_soul_root").write_text("marker\n", encoding="utf-8")
        if configs is None:
            configs = (
                ConfigurationFile(
                    name="main",
                    source_leaf="config.txt",
                    destination=HomeRelativeDestination(".config/example/config.txt"),
                ),
            )
        declaration = PlatformDeclaration(
            platform=Platform.LINUX,
            capabilities={},
            configurations=configs,
        )
        app = Application(id="example", display_name="Example", platforms=(declaration,))
        context = OperationContext(
            repository_root=root,
            platform=Platform.LINUX,
            host="fixture_host",
            target_account=TargetAccount("fixture_user", home or (root / "home"), True),
            conflict_policy=ConflictPolicy.BACKUP_AND_REPLACE,
        )
        for config in configs:
            source = root / "assimilation_directives/example/default/common" / config.source_leaf
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(f"canonical:{config.name}", encoding="utf-8")
        return app, declaration, context

    def test_apply_check_idempotent_unapply_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"

            applied = apply_config(app, declaration, context)
            self.assertEqual("applied", applied.code)
            self.assertTrue(applied.changed)
            self.assertTrue(destination.is_symlink())

            checked = check_config(app, declaration, context)
            self.assertEqual("applied", checked.code)
            self.assertEqual("applied", checked.data["structural_state"])
            self.assertTrue(checked.data["state_recorded"])
            self.assertEqual("managed", checked.data["ownership_state"])

            again = apply_config(app, declaration, context)
            self.assertEqual("applied", again.code)
            self.assertFalse(again.changed)

            unapplied = unapply_config(app, declaration, context)
            self.assertEqual("not_applied", unapplied.code)
            self.assertTrue(unapplied.changed)
            self.assertFalse(destination.exists())

    def test_check_distinguishes_structural_apply_from_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            source = root / "assimilation_directives/example/default/common/config.txt"
            destination = root / "home/.config/example/config.txt"
            destination.parent.mkdir(parents=True)
            os.symlink(source, destination)

            checked = check_config(app, declaration, context)

            self.assertEqual("applied", checked.code)
            self.assertEqual("applied", checked.data["structural_state"])
            self.assertFalse(checked.data["state_recorded"])
            self.assertEqual("unrecorded", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertTrue(destination.is_symlink())

    def test_check_reports_stale_state_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            self.assertTrue(apply_config(app, declaration, context).changed)
            destination.unlink()

            checked = check_config(app, declaration, context)

            self.assertEqual("not_applied", checked.code)
            self.assertEqual("not_applied", checked.data["structural_state"])
            self.assertTrue(checked.data["state_recorded"])
            self.assertEqual("stale_state", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertFalse(destination.exists())

    def test_check_reports_owned_relocation_without_repairing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            old_root = base / "old"
            new_root = base / "new"
            destination_home = base / "native_home"
            old_root.mkdir()
            app, declaration, context = self._build(old_root, home=destination_home)
            destination = destination_home / ".config/example/config.txt"
            self.assertTrue(apply_config(app, declaration, context).changed)
            raw_target = os.readlink(destination)
            old_root.rename(new_root)

            relocated_context = OperationContext(
                repository_root=new_root,
                platform=Platform.LINUX,
                host="fixture_host",
                target_account=TargetAccount("fixture_user", destination_home, True),
                conflict_policy=ConflictPolicy.ABORT,
            )
            checked = check_config(app, declaration, relocated_context)

            self.assertEqual("broken", checked.code)
            self.assertEqual("broken", checked.data["structural_state"])
            self.assertTrue(checked.data["state_recorded"])
            self.assertEqual("managed_stale_link", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertTrue(destination.is_symlink())
            self.assertEqual(raw_target, os.readlink(destination))

    def test_check_preserves_structural_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            destination.parent.mkdir(parents=True)
            destination.write_text("external", encoding="utf-8")

            checked = check_config(app, declaration, context)

            self.assertEqual("conflict", checked.code)
            self.assertEqual("conflict", checked.data["structural_state"])
            self.assertEqual("unrecorded", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertEqual("external", destination.read_text(encoding="utf-8"))

    def test_check_preserves_wrong_target_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            other = root / "other.txt"
            other.write_text("other", encoding="utf-8")
            destination.parent.mkdir(parents=True)
            os.symlink(other, destination)
            raw_target = os.readlink(destination)

            checked = check_config(app, declaration, context)

            self.assertEqual("wrong_target", checked.code)
            self.assertEqual("wrong_target", checked.data["structural_state"])
            self.assertEqual("unrecorded", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertEqual(raw_target, os.readlink(destination))

    def test_check_preserves_broken_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            missing = root / "missing.txt"
            destination.parent.mkdir(parents=True)
            os.symlink(missing, destination)
            raw_target = os.readlink(destination)

            checked = check_config(app, declaration, context)

            self.assertEqual("broken", checked.code)
            self.assertEqual("broken", checked.data["structural_state"])
            self.assertEqual("unrecorded", checked.data["ownership_state"])
            self.assertFalse(checked.changed)
            self.assertEqual(raw_target, os.readlink(destination))

    def test_existing_file_is_backed_up_and_restored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            destination.parent.mkdir(parents=True)
            destination.write_text("original", encoding="utf-8")

            result = apply_config(app, declaration, context)
            self.assertTrue(result.changed)
            self.assertEqual("canonical:main", destination.read_text(encoding="utf-8"))

            result = unapply_config(app, declaration, context)
            self.assertEqual("not_applied", result.code)
            self.assertFalse(destination.is_symlink())
            self.assertEqual("original", destination.read_text(encoding="utf-8"))

    def test_abort_conflict_does_not_mutate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            context = OperationContext(
                repository_root=context.repository_root,
                platform=context.platform,
                host=context.host,
                target_account=context.target_account,
                conflict_policy=ConflictPolicy.ABORT,
            )
            destination = root / "home/.config/example/config.txt"
            destination.parent.mkdir(parents=True)
            destination.write_text("original", encoding="utf-8")

            result = apply_config(app, declaration, context)
            self.assertEqual("conflict", result.code)
            self.assertFalse(result.changed)
            self.assertEqual("original", destination.read_text(encoding="utf-8"))

    def test_dry_run_is_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            context = OperationContext(
                repository_root=context.repository_root,
                platform=context.platform,
                host=context.host,
                target_account=context.target_account,
                dry_run=True,
                conflict_policy=ConflictPolicy.BACKUP_AND_REPLACE,
            )
            destination = root / "home/.config/example/config.txt"

            result = apply_config(app, declaration, context)
            self.assertEqual("would_apply", result.code)
            self.assertFalse(result.changed)
            self.assertFalse(destination.exists())

    def test_external_replacement_blocks_unapply(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            app, declaration, context = self._build(root)
            destination = root / "home/.config/example/config.txt"
            self.assertTrue(apply_config(app, declaration, context).changed)
            destination.unlink()
            destination.write_text("external", encoding="utf-8")

            result = unapply_config(app, declaration, context)
            self.assertEqual("conflict", result.code)
            self.assertFalse(result.changed)
            self.assertEqual("external", destination.read_text(encoding="utf-8"))

    def test_checkout_relocation_repairs_owned_stale_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            old_root = base / "old"
            new_root = base / "new"
            destination_home = base / "native_home"
            old_root.mkdir()
            app, declaration, context = self._build(old_root, home=destination_home)
            destination = destination_home / ".config/example/config.txt"

            self.assertTrue(apply_config(app, declaration, context).changed)
            old_root.rename(new_root)

            relocated_context = OperationContext(
                repository_root=new_root,
                platform=Platform.LINUX,
                host="fixture_host",
                target_account=TargetAccount("fixture_user", destination_home, True),
                conflict_policy=ConflictPolicy.ABORT,
            )
            repaired = apply_config(app, declaration, relocated_context)
            self.assertEqual("applied", repaired.code)
            self.assertTrue(repaired.changed)
            self.assertEqual(
                (new_root / "assimilation_directives/example/default/common/config.txt").resolve(),
                destination.resolve(),
            )

            self.assertEqual(
                "not_applied",
                unapply_config(app, declaration, relocated_context).code,
            )

    def test_multi_file_apply_rolls_back_earlier_target_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            configs = (
                ConfigurationFile(
                    name="one",
                    source_leaf="one.txt",
                    destination=HomeRelativeDestination("one/config.txt"),
                ),
                ConfigurationFile(
                    name="two",
                    source_leaf="two.txt",
                    destination=HomeRelativeDestination("two/config.txt"),
                ),
            )
            app, declaration, context = self._build(root, configs=configs)
            first = root / "home/one/config.txt"
            second = root / "home/two/config.txt"
            second.mkdir(parents=True)

            result = apply_config(app, declaration, context)
            self.assertEqual("conflict_directory", result.code)
            self.assertFalse(first.exists())
            self.assertTrue(second.is_dir())


if __name__ == "__main__":
    unittest.main()
