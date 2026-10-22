# SPDX-License-Identifier: GPL-2.0-or-later
"""Staging safety and owner-source precedence checks."""

import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from prepare_baseline import prepare, unpack


def archive(name, content):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as output:
        output.writestr(name, content)
    return zipfile.ZipFile(io.BytesIO(data.getvalue()))


class BaselineStagingTests(unittest.TestCase):
    def test_invalid_overlay_does_not_create_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(ValueError, "failed verification"):
                prepare(root / "missing-legacy", root, root / "destination")
            self.assertFalse((root / "destination").exists())

    def test_invalid_overlay_does_not_change_existing_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            destination = root / "previous-good"
            destination.mkdir()
            previous = destination / "XboxMain.cpp"
            previous.write_bytes(b"last good source")
            with self.assertRaises(ValueError):
                prepare(root / "missing-legacy", root, destination)
            self.assertEqual(previous.read_bytes(), b"last good source")

    def test_owner_overlay_wins_and_receipt_matches_final_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp)
            manifest = {}
            with archive("Xbox/XboxMain.cpp", b"old donor") as donor:
                unpack(donor, destination, manifest, "legacy")
            with archive("Xbox/XboxMain.cpp", b"authentic owner") as owner:
                unpack(owner, destination, manifest, "owner")
            self.assertEqual((destination / "Xbox/XboxMain.cpp").read_bytes(), b"authentic owner")
            self.assertEqual(manifest["Xbox/XboxMain.cpp"]["origin"], "owner")
            self.assertEqual(manifest["Xbox/XboxMain.cpp"]["sha256"],
                             hashlib.sha256(b"authentic owner").hexdigest())

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("../escaped.cpp", "/absolute.cpp", "C:/drive.cpp", "..\\escaped.cpp"):
                with self.subTest(name=name), archive(name, b"untrusted") as source:
                    with self.assertRaisesRegex(ValueError, "Unsafe archive path"):
                        unpack(source, root, {}, "fixture")
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
