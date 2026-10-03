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


if __name__ == "__main__":
    unittest.main()
