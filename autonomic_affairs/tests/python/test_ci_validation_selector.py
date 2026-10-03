"""Tests for CI check selection and runner coalescing."""

import unittest

from autonomic_affairs.ci_validation_selector import (
    GROUP_ALIASES,
    REGISTERED_CHECKS,
    PolicySelection,
    parse_selector,
    runner_groups_for_checks,
)


EXPECTED_CHECKS = (
    "linux-python",
    "linux-applications",
    "linux-install",
    "linux-session",
    "linux-matrix",
    "windows-python",
    "windows-applications",
    "windows-posix",
    "windows-install",
    "fresh-linux",
    "fresh-windows",
    "codeql-python",
    "codeql-actions",
)


class ValidationSelectorTests(unittest.TestCase):
    def assert_all(self, selection):
        self.assertEqual(EXPECTED_CHECKS, selection.selected)
        self.assertFalse(selection.automatic)

    def test_registry_is_stable(self):
        self.assertEqual(EXPECTED_CHECKS, REGISTERED_CHECKS)
        self.assertEqual(EXPECTED_CHECKS[:5], GROUP_ALIASES["linux"])
        self.assertEqual(EXPECTED_CHECKS[5:9], GROUP_ALIASES["windows"])

    def test_policy_selection_exposes_automatic_mode(self):
        selection = PolicySelection((), True, "test", automatic=True)
        self.assertTrue(selection.automatic)

    def test_missing_selector_defaults_to_all_for_explicit_context(self):
        selection = parse_selector(None, source="test")
        self.assertTrue(selection.valid)
        self.assert_all(selection)

    def test_missing_selector_can_request_automatic_mode(self):
        selection = parse_selector(None, source="test", default_auto=True)
        self.assertTrue(selection.valid)
        self.assertTrue(selection.automatic)
        self.assertEqual((), selection.selected)

    def test_auto_all_and_none(self):
        auto = parse_selector("auto", source="test")
        all_selection = parse_selector("all", source="test")
        none = parse_selector("none", source="test")
        self.assertTrue(auto.valid)
        self.assertTrue(auto.automatic)
        self.assertEqual((), auto.selected)
        self.assert_all(all_selection)
        self.assertTrue(none.valid)
        self.assertFalse(none.automatic)
        self.assertEqual((), none.selected)

    def test_group_and_exact_selection_expand_and_normalize(self):
        selection = parse_selector(
            " windows,linux-python,codeql-python,windows-python,linux-python ",
            source="test",
        )
        self.assertTrue(selection.valid)
        self.assertEqual(
            (
                "linux-python",
                "windows-python",
                "windows-applications",
                "windows-posix",
                "windows-install",
                "codeql-python",
            ),
            selection.selected,
        )

    def test_unknown_selector_fails_safe_to_all(self):
        selection = parse_selector("linux,banana", source="test")
        self.assertFalse(selection.valid)
        self.assert_all(selection)
        self.assertIn("banana", selection.error)

    def test_empty_token_fails_safe_to_all(self):
        selection = parse_selector("linux,,windows", source="test")
        self.assertFalse(selection.valid)
        self.assert_all(selection)

    def test_standalone_tokens_cannot_be_mixed(self):
        for value in ("all,linux", "none,windows", "auto,linux-python"):
            with self.subTest(value=value):
                selection = parse_selector(value, source="test")
                self.assertFalse(selection.valid)
                self.assert_all(selection)

    def test_runner_groups_coalesce_compatible_checks(self):
        groups = runner_groups_for_checks(
            ("linux-python", "linux-session", "fresh-windows", "codeql-python")
        )
        self.assertEqual(
            {
                "linux": ("linux-python", "linux-session"),
                "fresh-windows": ("fresh-windows",),
                "codeql-python": ("codeql-python",),
            },
            groups,
        )


import subprocess
import tempfile
from pathlib import Path

from autonomic_affairs.ci_validation_selector import (
    PolicyEvidenceError,
    checks_for_paths,
    git_changed_paths,
    resolve_automatic_event,
    validate_commit_summary,
)


class PathClassificationTests(unittest.TestCase):
    def test_inert_task_markdown_selects_no_downstream_checks(self):
        selection = checks_for_paths(("autonomic_affairs/tasks/MSHP-X/example.md",))
        self.assertTrue(selection.valid)
        self.assertEqual((), selection.selected)

    def test_runtime_python_selects_cross_platform_python_and_codeql(self):
        selection = checks_for_paths(("annexation_procedures/runtime.py",))
        self.assertEqual(
            ("linux-python", "windows-python", "codeql-python"),
            selection.selected,
        )

    def test_install_surface_selects_all_blocking_plus_python_codeql(self):
        selection = checks_for_paths(("annexation_procedures/fish/install.py",))
        expected = tuple(c for c in EXPECTED_CHECKS if c != "codeql-actions")
        self.assertEqual(expected, selection.selected)

    def test_noncontrol_actions_workflow_selects_actions_codeql(self):
        selection = checks_for_paths((".github/workflows/release.yml",))
        self.assertEqual(("codeql-actions",), selection.selected)

    def test_central_ci_control_selects_everything(self):
        selection = checks_for_paths((".github/workflows/machine_soul_validation.yml",))
        self.assertEqual(EXPECTED_CHECKS, selection.selected)
        self.assertFalse(selection.automatic)

    def test_unknown_path_fails_safe_to_everything(self):
        selection = checks_for_paths(("mystery.payload",))
        self.assertEqual(EXPECTED_CHECKS, selection.selected)
        self.assertFalse(selection.automatic)
        self.assertEqual("path-classifier-fallback", selection.source)

    def test_path_classification_unions_relevance(self):
        selection = checks_for_paths((
            "autonomic_affairs/tasks/MSHP-X/example.md",
            "annexation_procedures/runtime.py",
            ".github/workflows/release.yml",
        ))
        self.assertEqual(
            ("linux-python", "windows-python", "codeql-python", "codeql-actions"),
            selection.selected,
        )

    def test_existing_linux_application_test_maps_to_shared_and_fresh_checks(self):
        selection = checks_for_paths((
            "autonomic_affairs/tests/applications/test_linux_operations.sh",
        ))
        self.assertEqual(("linux-applications", "fresh-linux"), selection.selected)


class GitRangeTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.strip()

    def _commit(self, root: Path, message: str) -> str:
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", message)
        return self._git(root, "rev-parse", "HEAD")

    def _repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        self._git(root, "init")
        self._git(root, "config", "user.email", "tests@example.invalid")
        self._git(root, "config", "user.name", "Tests")
        return temp, root

    def test_two_dot_range_covers_multi_commit_push(self):
        temp, root = self._repo()
        with temp:
            (root / "base.txt").write_text("base", encoding="utf-8")
            base = self._commit(root, "[Test] Base")
            (root / "a.py").write_text("a", encoding="utf-8")
            self._commit(root, "[Test] A")
            (root / "b.py").write_text("b", encoding="utf-8")
            head = self._commit(root, "[Test] B")
            self.assertEqual(
                ("a.py", "b.py"),
                git_changed_paths(base, head, cwd=root),
            )

    def test_three_dot_range_uses_merge_base(self):
        temp, root = self._repo()
        with temp:
            (root / "base.txt").write_text("base", encoding="utf-8")
            self._commit(root, "[Test] Base")
            self._git(root, "branch", "feature")
            (root / "main-only.txt").write_text("main", encoding="utf-8")
            main = self._commit(root, "[Test] Main")
            self._git(root, "checkout", "feature")
            (root / "feature-only.py").write_text("feature", encoding="utf-8")
            head = self._commit(root, "[Test] Feature")
            self.assertEqual(
                ("feature-only.py",),
                git_changed_paths(main, head, three_dot=True, cwd=root),
            )

    def test_rename_returns_old_and_new_paths(self):
        temp, root = self._repo()
        with temp:
            (root / "old.txt").write_text("same", encoding="utf-8")
            base = self._commit(root, "[Test] Base")
            self._git(root, "mv", "old.txt", "new.py")
            head = self._commit(root, "[Test] Rename")
            self.assertEqual(
                ("old.txt", "new.py"),
                git_changed_paths(base, head, cwd=root),
            )

    def test_missing_git_object_is_policy_evidence_error(self):
        temp, root = self._repo()
        with temp:
            (root / "a").write_text("a", encoding="utf-8")
            head = self._commit(root, "[Test] Base")
            with self.assertRaises(PolicyEvidenceError):
                git_changed_paths("0" * 40, head, cwd=root)


class MetadataAndEventTests(unittest.TestCase):
    def test_commit_summary_grammar(self):
        for summary in ("[Feature][CI] Add policy", "[Fix] Repair thing"):
            with self.subTest(summary=summary):
                self.assertIsNone(validate_commit_summary(summary))
        for summary in ("Feature: nope", "[Banana] Nope", "[Fix][] Nope", "[Fix]"):
            with self.subTest(summary=summary):
                self.assertIsNotNone(validate_commit_summary(summary))

    def test_forced_push_auto_falls_back_to_all(self):
        selection = resolve_automatic_event(
            "push",
            commit_message="[Fix] Example",
            before="1" * 40,
            after="2" * 40,
            forced=True,
        )
        self.assertTrue(selection.valid)
        self.assertEqual(EXPECTED_CHECKS, selection.selected)
        self.assertFalse(selection.automatic)

    def test_valid_explicit_override_wins_over_forced_push(self):
        selection = resolve_automatic_event(
            "push",
            commit_message="[Fix] Example\n\nCI: none\n",
            before="1" * 40,
            after="2" * 40,
            forced=True,
        )
        self.assertTrue(selection.valid)
        self.assertEqual((), selection.selected)
        self.assertFalse(selection.automatic)


if __name__ == "__main__":
    unittest.main()
