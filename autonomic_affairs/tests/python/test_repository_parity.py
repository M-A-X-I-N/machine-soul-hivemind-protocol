from __future__ import annotations

from pathlib import Path
import unittest


class RepositoryParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[3]

    def test_static_host_inventory_is_absent(self) -> None:
        self.assertFalse((self.root / "hosts").exists())

    def test_legacy_shared_shell_runtime_is_absent(self) -> None:
        self.assertFalse(
            (self.root / "accumulated_instruments" / "configuration_deployment").exists()
        )

    def test_annexation_runtime_is_platform_neutral_python(self) -> None:
        annexation = self.root / "annexation_procedures"
        applications = [
            path
            for path in annexation.iterdir()
            if path.is_dir() and (path / "_application.py").is_file()
        ]
        self.assertGreater(len(applications), 0)

        for application in applications:
            with self.subTest(application=application.name):
                self.assertFalse((application / "linux").exists())
                self.assertFalse((application / "windows").exists())

                runtime_non_python = [
                    path.name
                    for path in application.iterdir()
                    if path.is_file()
                    and path.suffix in {".sh", ".ps1", ".bat", ".cmd"}
                ]
                self.assertEqual([], runtime_non_python)

    def test_native_process_scripts_are_not_production_policy_engines(self) -> None:
        ignored_roots = {
            self.root / "autonomic_affairs" / "tests",
            self.root / "assimilation_directives",
        }
        offenders = []
        for suffix in ("*.sh", "*.ps1"):
            for path in self.root.rglob(suffix):
                if any(root == path or root in path.parents for root in ignored_roots):
                    continue
                offenders.append(path.relative_to(self.root).as_posix())

        self.assertEqual([], sorted(offenders))

    def test_root_marker_and_autonomic_namespace_exist(self) -> None:
        self.assertTrue((self.root / ".machine_soul_root").is_file())
        self.assertTrue((self.root / "autonomic_affairs").is_dir())
        self.assertFalse((self.root / "collective_affairs").exists())


if __name__ == "__main__":
    unittest.main()
