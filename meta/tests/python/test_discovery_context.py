from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from annexation_procedures.discovery import (
    DiscoveryError,
    UnsupportedTargetAccount,
    build_operation_context,
    discover_host,
    resolve_repository_root,
    resolve_target_account,
)
from annexation_procedures.model import Platform


class DiscoveryTests(unittest.TestCase):
    def test_repository_root_uses_stable_marker(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".machine_soul_root").write_text("marker\n", encoding="utf-8")
            nested = root / "a" / "b"
            nested.mkdir(parents=True)
            self.assertEqual(root, resolve_repository_root(nested, environ={}))

    def test_invalid_explicit_repository_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(DiscoveryError):
                resolve_repository_root(environ={"MACHINE_SOUL": raw})

    def test_host_override_is_normalized(self) -> None:
        self.assertEqual("fixture-host", discover_host(environ={"MACHINE_SOUL_HOST": "Fixture-HOST"}))

    def test_non_current_windows_target_is_explicitly_unsupported(self) -> None:
        current = os.environ.get("USERNAME") or os.environ.get("USER") or "current"
        with self.assertRaises(UnsupportedTargetAccount):
            resolve_target_account(
                current + "-someone-else",
                platform=Platform.WINDOWS,
                environ={"USERNAME": current, "USERPROFILE": "C:\\Users\\current"},
            )

    def test_build_context_validates_root_and_resolves_current_account(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".machine_soul_root").write_text("marker\n", encoding="utf-8")
            context = build_operation_context(repository_root=root, host="Synthetic-HOST")
            self.assertEqual(root, context.repository_root)
            self.assertEqual("synthetic-host", context.host)
            self.assertTrue(context.target_account.is_current)


if __name__ == "__main__":
    unittest.main()
