#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Check every object member of the six Xbox FFmpeg static libraries for PPCBE."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

LIBRARIES = ("avcodec", "avdevice", "avformat", "avutil", "swresample", "swscale")


def check_archive(data):
    if not data.startswith(b"!<arch>\n"):
        raise ValueError("Not a COFF archive")
    offset, objects = 8, 0
    while offset < len(data):
        header = data[offset:offset + 60]
        if len(header) != 60 or header[58:] != b"`\n":
            raise ValueError("Invalid archive member header")
        name, size = header[:16].decode("ascii").strip(), int(header[48:58])
        body = data[offset + 60:offset + 60 + size]
        if len(body) != size:
            raise ValueError("Truncated archive member")
        if name not in ("/", "//", "/SYM64/"):
            if len(body) < 20 or struct.unpack("<H", body[:2])[0] != 0x1F2:
                raise ValueError("Object is not Xbox PPCBE: " + name)
            objects += 1
        offset += 60 + size + size % 2
    if not objects:
        raise ValueError("Archive contains no object files")
    return objects


def verify(directory):
    records = []
    for name in LIBRARIES:
        path = directory / (name + ".lib")
        data = path.read_bytes()
        records.append({"name": path.name, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "ppcbe_objects": check_archive(data)})
    return {"status": "PASS", "machine": "0x01F2 PPCBE", "libraries": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.directory), indent=2))
