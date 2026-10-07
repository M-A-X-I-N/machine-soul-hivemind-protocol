from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from annexation.filesystem import LinkStatus, classify_link


class FilesystemTests(unittest.TestCase):
    def test_link_classification(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source"
            source.write_text("canonical", encoding="utf-8")
            destination = root / "destination"

            self.assertEqual(LinkStatus.NOT_APPLIED, classify_link(source, destination).status)

            destination.write_text("unmanaged", encoding="utf-8")
            self.assertEqual(LinkStatus.CONFLICT, classify_link(source, destination).status)
            destination.unlink()

            destination.symlink_to(source)
            self.assertEqual(LinkStatus.APPLIED, classify_link(source, destination).status)
            destination.unlink()

            other = root / "other"
            other.write_text("other", encoding="utf-8")
            destination.symlink_to(other)
            self.assertEqual(LinkStatus.WRONG_TARGET, classify_link(source, destination).status)
            destination.unlink()

            missing = root / "missing"
            destination.symlink_to(missing)
            self.assertEqual(LinkStatus.BROKEN, classify_link(source, destination).status)


if __name__ == "__main__":
    unittest.main()
