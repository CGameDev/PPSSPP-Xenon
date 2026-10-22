#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Count diagnostic emissions, excluding MSBuild's repeated final summary."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def audit(text):
    emissions = []
    for line in text.splitlines():
        if line.strip() in ("Build succeeded.", "Build FAILED."):
            break
        match = re.search(r"\bwarning ([A-Z]+\d+):\s*(.*)", line)
        if match:
            emissions.append({"code": match[1], "diagnostic": line.strip()})
    counts = dict(sorted(Counter(item["code"] for item in emissions).items()))
    return {"total": len(emissions), "by_code": counts,
            "targeted_62_codes": sum(counts.get(code, 0) for code in ("C4742", "C4744", "C4715")),
            "emissions": emissions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    payload = args.log.read_bytes()
    encoding = "utf-16" if payload.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    print(json.dumps(audit(payload.decode(encoding)), indent=2))


if __name__ == "__main__":
    main()
