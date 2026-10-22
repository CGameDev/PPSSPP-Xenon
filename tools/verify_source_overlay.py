#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only gate for the owner's archived Xbox source. Never extracts files."""

import argparse
import base64
import binascii
import hashlib
import io
import json
from pathlib import Path
import zipfile
import zlib


EXPECTED_SHA256 = "6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35"
PART_NAMES = tuple(f"Xbox-original-upload.part{i:02d}.b64" for i in range(1, 5))
MAX_ENCODED_BYTES = 8 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
REQUIRED_FILES = {"Xbox/XboxMain.cpp", "Xbox/XboxLauncher.cpp", "Xbox/PPSSPP.sln"}


def inspect_archive(payload, expected_sha256):
    """CRC checks are diagnostic only; they cannot override a digest mismatch."""
    actual = hashlib.sha256(payload).hexdigest()
    result = {
        "decoded_bytes": len(payload),
        "expected_sha256": expected_sha256,
        "actual_sha256": actual,
        "sha256_matches": actual == expected_sha256,
        "zip_crc": "NOT_RUN",
        "errors": [],
    }
    if actual != expected_sha256:
        result["errors"].append("SHA-256 mismatch: do not extract, import or build this overlay.")
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            members = archive.infolist()
            result["archive_members"] = len(members)
            if len(members) > 4096 or sum(x.file_size for x in members) > MAX_EXPANDED_BYTES:
                raise ValueError("Archive exceeds diagnostic limits")
            missing = sorted(REQUIRED_FILES - set(archive.namelist()))
            if missing:
                result["errors"].append("Missing required files: " + ", ".join(missing))
            bad_members = []
            for member in members:
                try:
                    with archive.open(member) as stream:
                        while stream.read(65536):
                            pass
                except (zipfile.BadZipFile, zlib.error, EOFError, RuntimeError, NotImplementedError) as error:
                    bad_members.append({"name": member.filename, "error": str(error)})
            result["bad_members"] = bad_members
            result["zip_crc"] = "FAIL" if bad_members else "PASS"
            if bad_members:
                result["errors"].append("ZIP member verification failed; archive is damaged.")
    except (zipfile.BadZipFile, ValueError, OSError) as error:
        result["zip_crc"] = "FAIL"
        result["errors"].append(str(error))
    result["status"] = "FAIL" if result["errors"] else "PASS"
    return result


def verify_overlay(directory):
    result = {"schema_version": 1, "read_only": True, "parts": [], "errors": []}
    try:
        chunks = []
        total = 0
        for name in PART_NAMES:
            path = directory / name
            size = path.stat().st_size
            total += size
            if total > MAX_ENCODED_BYTES:
                raise ValueError("Encoded overlay exceeds diagnostic limit")
            raw = path.read_bytes()
            result["parts"].append({"name": name, "bytes": len(raw),
                                    "sha256": hashlib.sha256(raw).hexdigest()})
            # Strip only ASCII transport whitespace. Reject other non-base64 bytes.
            chunks.append(b"".join(raw.split()))
        payload = base64.b64decode(b"".join(chunks), validate=True)
        result.update(inspect_archive(payload, EXPECTED_SHA256))
    except (OSError, ValueError, binascii.Error) as error:
        result["errors"].append(str(error))
        result["status"] = "FAIL"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path,
                        default=Path(__file__).resolve().parents[1] / "source-overlay")
    args = parser.parse_args()
    report = verify_overlay(args.overlay)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
