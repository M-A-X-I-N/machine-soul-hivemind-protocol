from __future__ import annotations

from pathlib import Path
import tempfile
import textwrap
import unittest

from annexation.applications import (
    ApplicationLoadError,
    discover_applications,
    load_application,
)


class ApplicationLoadingTests(unittest.TestCase):
    def _write_declaration(self, path: Path, app_id: str) -> None:
        path.write_text(
            textwrap.dedent(
                f"""
                from annexation.model import Application
                APPLICATION = Application(id={app_id!r}, display_name={app_id!r}, platforms=())
                """
            ),
            encoding="utf-8",
        )

    def test_load_application_requires_application_constant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "_application.py"
            path.write_text("THING = 1\n", encoding="utf-8")
            with self.assertRaises(ApplicationLoadError):
                load_application(path)

    def test_discovery_is_sorted_and_ignores_apps_without_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            annexation = root / "annexation"
            for name in ("zeta", "alpha", "ignored"):
                (annexation / name).mkdir(parents=True)
            self._write_declaration(annexation / "zeta" / "_application.py", "zeta")
            self._write_declaration(annexation / "alpha" / "_application.py", "alpha")

            self.assertEqual(
                ("alpha", "zeta"),
                tuple(app.id for app in discover_applications(root)),
            )


if __name__ == "__main__":
    unittest.main()
