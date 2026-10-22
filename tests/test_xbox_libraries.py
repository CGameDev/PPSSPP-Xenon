# SPDX-License-Identifier: GPL-2.0-or-later
import struct
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_xbox_libraries import check_archive


def archive(machine):
    body = struct.pack("<HHIIIHH", machine, 1, 0, 0, 0, 0, 0)
    header = b"one.o/          " + b"0           " + b"0     " + b"0     " + b"644     " + str(len(body)).encode().ljust(10) + b"`\n"
    return b"!<arch>\n" + header + body


class XboxLibraryTests(unittest.TestCase):
    def test_ppcbe_accepted(self):
        self.assertEqual(check_archive(archive(0x1F2)), 1)

    def test_host_object_rejected(self):
        with self.assertRaisesRegex(ValueError, "not Xbox PPCBE"):
            check_archive(archive(0x14C))

    def test_truncated_archive_rejected(self):
        with self.assertRaisesRegex(ValueError, "Truncated"):
            check_archive(archive(0x1F2)[:-2])

    def test_empty_archive_rejected(self):
        with self.assertRaisesRegex(ValueError, "no object"):
            check_archive(b"!<arch>\n")


if __name__ == "__main__":
    unittest.main()
