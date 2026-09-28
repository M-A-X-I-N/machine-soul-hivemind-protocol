"""Tests for explicit CI validation selection."""

import unittest

from autonomic_affairs.ci_validation_selector import (
    REGISTERED_VALIDATION_SETS,
    parse_selector,
    resolve_event_selection,
    selector_from_commit_message,
)


class ValidationSelectorTests(unittest.TestCase):
    def assert_all(self, selection):
        self.assertEqual(REGISTERED_VALIDATION_SETS, selection.selected)

    def test_missing_selector_defaults_to_all(self):
        selection = parse_selector(None, source="test")
        self.assertTrue(selection.valid)
        self.assert_all(selection)

    def test_all_and_none(self):
        all_selection = parse_selector("all", source="test")
        none_selection = parse_selector("none", source="test")
        self.assertTrue(all_selection.valid)
        self.assert_all(all_selection)
        self.assertTrue(none_selection.valid)
        self.assertEqual((), none_selection.selected)

    def test_subset_normalizes_whitespace_duplicates_and_order(self):
        selection = parse_selector(
            " fresh-windows, linux,linux ",
            source="test",
        )
        self.assertTrue(selection.valid)
        self.assertEqual(("linux", "fresh-windows"), selection.selected)

    def test_unknown_selector_fails_safe_to_all(self):
        selection = parse_selector("linux,banana", source="test")
        self.assertFalse(selection.valid)
        self.assert_all(selection)
        self.assertIn("banana", selection.error)

    def test_empty_token_fails_safe_to_all(self):
        selection = parse_selector("linux,,windows", source="test")
        self.assertFalse(selection.valid)
        self.assert_all(selection)

    def test_all_or_none_cannot_be_mixed(self):
        for value in ("all,linux", "none,windows"):
            with self.subTest(value=value):
                selection = parse_selector(value, source="test")
                self.assertFalse(selection.valid)
                self.assert_all(selection)

    def test_push_uses_ci_line_from_tip_message(self):
        selection = resolve_event_selection(
            "push",
            commit_message=(
                "[Fix][Thing] Example\n\n"
                "Agent-authored-by: Example\n"
                "CI: windows, fresh-windows\n"
            ),
        )
        self.assertTrue(selection.valid)
        self.assertEqual(("windows", "fresh-windows"), selection.selected)
        self.assertEqual("commit-trailer", selection.source)

    def test_push_without_ci_line_defaults_to_all(self):
        selection = resolve_event_selection(
            "push",
            commit_message="[Feature] Nothing special\n\nBody text.",
        )
        self.assertTrue(selection.valid)
        self.assert_all(selection)
        self.assertEqual("main-default", selection.source)

    def test_multiple_ci_lines_fail_safe(self):
        selection = selector_from_commit_message(
            "CI: linux\n\nSomething\n\nCI: windows\n"
        )
        self.assertFalse(selection.valid)
        self.assert_all(selection)

    def test_manual_dispatch_uses_explicit_selector(self):
        selection = resolve_event_selection(
            "workflow_dispatch",
            manual_selector="linux,fresh-linux",
        )
        self.assertTrue(selection.valid)
        self.assertEqual(("linux", "fresh-linux"), selection.selected)

    def test_other_events_default_to_all(self):
        selection = resolve_event_selection("pull_request")
        self.assertTrue(selection.valid)
        self.assert_all(selection)


if __name__ == "__main__":
    unittest.main()
