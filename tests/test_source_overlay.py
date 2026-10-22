# SPDX-License-Identifier: GPL-2.0-or-later
"""Safety checks use disposable synthetic archives, never repaired owner source."""

import base64
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import verify_source_overlay as gate


def fixture_zip():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(gate.REQUIRED_FILES):
            archive.writestr(name, b"synthetic source fixture")
    return stream.getvalue()


class SourceGateTests(unittest.TestCase):
    def test_valid_archive_requires_matching_hash(self):
        data = fixture_zip()
        report = gate.inspect_archive(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["zip_crc"], "PASS")

    def test_crc_success_cannot_override_wrong_hash(self):
        report = gate.inspect_archive(fixture_zip(), gate.EXPECTED_SHA256)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["zip_crc"], "PASS")

    def test_matching_hash_cannot_override_corrupt_member(self):
        data = fixture_zip().replace(b"synthetic source fixture", b"damaged!! source fixture", 1)
        report = gate.inspect_archive(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["zip_crc"], "FAIL")
        self.assertEqual(len(report["bad_members"]), 1)

    def test_non_zip_rejected(self):
        data = b"not a zip"
        self.assertEqual(gate.inspect_archive(data, hashlib.sha256(data).hexdigest())["status"], "FAIL")

    def test_missing_required_source_rejected(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("unrelated.txt", "fixture")
        data = stream.getvalue()
        self.assertEqual(gate.inspect_archive(data, hashlib.sha256(data).hexdigest())["status"], "FAIL")

    def test_missing_part_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(gate.verify_overlay(Path(temp))["status"], "FAIL")

    def test_invalid_base64_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in gate.PART_NAMES:
                (root / name).write_bytes(b"!!!!")
            self.assertEqual(gate.verify_overlay(root)["status"], "FAIL")

    def test_cli_is_read_only_and_fails_for_untrusted_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            encoded = base64.b64encode(fixture_zip())
            # Transport line breaks and padding belong to the concatenated stream.
            step = len(encoded) // 4
            for i, name in enumerate(gate.PART_NAMES):
                chunk = encoded[i * step:(i + 1) * step] if i < 3 else encoded[i * step:]
                (root / name).write_bytes(b"\r\n" + chunk + b"\n")
            (root / "extracted").mkdir()
            (root / "extracted" / "preserve.txt").write_text("last good source")
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            run = subprocess.run([sys.executable, str(Path(gate.__file__)), "--overlay", str(root)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('"sha256_matches": false', run.stdout)
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_encoded_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / gate.PART_NAMES[0]).write_bytes(b"AAAA")
            with patch.object(gate, "MAX_ENCODED_BYTES", 3):
                self.assertEqual(gate.verify_overlay(root)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
