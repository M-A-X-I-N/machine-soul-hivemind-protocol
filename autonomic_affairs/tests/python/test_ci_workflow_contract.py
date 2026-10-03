from pathlib import Path
import unittest


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[3]
        cls.workflows = cls.root / ".github" / "workflows"

    def text(self, name):
        return (self.workflows / name).read_text(encoding="utf-8")

    def test_linux_workflow_uses_one_runner_and_stable_conditional_checks(self):
        text = self.text("machine_soul_validation_linux.yml")
        self.assertEqual(1, text.count("runs-on:"))
        self.assertIn("checks_json:", text)
        self.assertIn("actions/checkout@v7", text)
        for check_id in (
            "linux-python",
            "linux-applications",
            "linux-install",
            "linux-session",
            "linux-matrix",
        ):
            self.assertEqual(1, text.count(f"name: Check {check_id}"))
            self.assertIn(
                f"contains(fromJSON(inputs.checks_json), '{check_id}')",
                text,
            )

    def test_windows_workflow_uses_one_runner_and_stable_conditional_checks(self):
        text = self.text("machine_soul_validation_windows.yml")
        self.assertEqual(1, text.count("runs-on:"))
        self.assertIn("checks_json:", text)
        self.assertIn("actions/checkout@v7", text)
        for check_id in (
            "windows-python",
            "windows-applications",
            "windows-posix",
            "windows-install",
        ):
            self.assertEqual(1, text.count(f"name: Check {check_id}"))
            self.assertIn(
                f"contains(fromJSON(inputs.checks_json), '{check_id}')",
                text,
            )

    def test_fresh_workflows_expose_one_stable_check_each(self):
        for filename, check_id in (
            ("machine_soul_validation_fresh_linux.yml", "fresh-linux"),
            ("machine_soul_validation_fresh_windows.yml", "fresh-windows"),
        ):
            with self.subTest(filename=filename):
                text = self.text(filename)
                self.assertEqual(1, text.count("runs-on:"))
                self.assertIn("checks_json:", text)
                self.assertEqual(1, text.count(f"name: Check {check_id}"))
                self.assertIn(
                    f"contains(fromJSON(inputs.checks_json), '{check_id}')",
                    text,
                )


if __name__ == "__main__":
    unittest.main()
