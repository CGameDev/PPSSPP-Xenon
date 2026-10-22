# SPDX-License-Identifier: GPL-2.0-or-later
"""Local kit integrity, path confinement and no-overwrite checks; no Xbox APIs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from prepare_smoke_test import prepare, sha, verify_kit


class SmokePackageTests(unittest.TestCase):
    def test_payload_corruption_fails_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / 'xx.xex'
            data.write_bytes(b'candidate fixture')
            (root / 'MANIFEST.json').write_text(json.dumps(dict(files=[dict(
                path='xx.xex', bytes=data.stat().st_size, sha256=sha(data))], required_directories=[])))
            self.assertEqual(verify_kit(root), 1)
            data.write_bytes(b'corrupted fixture')
            with self.assertRaisesRegex(ValueError, 'hash/size mismatch'):
                verify_kit(root)

    def test_manifest_cannot_read_outside_kit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'kit'
            root.mkdir()
            (root / 'MANIFEST.json').write_text(json.dumps(dict(files=[dict(
                path='../other-file', bytes=0, sha256='')], required_directories=[])))
            with self.assertRaises(ValueError):
                verify_kit(root)

    def test_existing_output_is_preserved_before_inputs_are_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'kit'
            root.mkdir()
            marker = root / 'owner-save'
            marker.write_bytes(b'preserve')
            with self.assertRaisesRegex(ValueError, 'Fresh destination'):
                prepare(root, Path(temp) / 'absent', Path(temp) / 'absent')
            self.assertEqual(marker.read_bytes(), b'preserve')
            self.assertEqual(list(root.iterdir()), [marker])


if __name__ == '__main__':
    unittest.main()
