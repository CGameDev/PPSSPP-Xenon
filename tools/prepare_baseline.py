#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Assemble pinned legacy sources with the verified owner overlay in fresh staging."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile
import shutil

from verify_source_overlay import PART_NAMES, verify_overlay

LEGACY_COMMIT = "540db97d96136b2139e5f12dd3c0bb18f2e1cd1f"


def unpack(archive, destination, manifest, origin):
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or ":" in info.filename or "\\" in info.filename:
            raise ValueError("Unsafe archive path: " + info.filename)
        if info.is_dir():
            continue
        target = destination.joinpath(*path.parts)
        payload = archive.read(info)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        manifest[info.filename] = {"origin": origin, "sha256": hashlib.sha256(payload).hexdigest(),
                                   "bytes": len(payload)}


def apply_build_compatibility(destination, project):
    # The patches are tracked separately; the archival owner bytes stay pristine.
    relative = destination.relative_to(project).as_posix()
    for name in (
        'Xbox/XboxLauncher.cpp',
        'Xbox/xx/xx.vcxproj',
        'GPU/GPUState.h',
        'Common/FileUtil.cpp',
        'Common/MemArena.cpp',
        'Common/ppcEmitter.cpp',
        'Core/HLE/sceKernelModule.cpp',
        'Core/HLE/sceAtrac.cpp',
        'Core/Dialog/SavedataParam.cpp',
        'GPU/Directx9/helper/global.cpp',
        'Core/MIPS/PPC/PpcCompVFPU.cpp',
        'Core/MIPS/JitCommon/JitBlockCache.h',
        'Core/MIPS/PPC/PpcJit.cpp',
        'GPU/Directx9/VertexDecoderDX9.cpp',
        'GPU/Directx9/FramebufferDX9.cpp',
        'ext/xxhash.c',
        'Common/CommonXbox.vcxproj',
        'Core/CoreXbox.vcxproj',
        'GPU/GPUXbox.vcxproj',
        'Xbox/XboxMain.cpp',
    ):
        path = destination / name
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    git = ["git", "-c", "safe.directory=" + project.as_posix(), "-C", str(project), "apply"]
    for name in ("launcher-legacy-compat.patch", "local-build-project.patch", "warning-fixes.patch", "remaining-warnings.patch"):
        patch = project / "baseline-overlay" / name
        subprocess.run(git + ["--check", "--directory=" + relative, str(patch)], check=True)
        subprocess.run(git + ["--directory=" + relative, str(patch)], check=True)
    for name in ("XenonStateDeleteCompat.h", "XenonEmulationLoop.h"):
        shutil.copyfile(project / "baseline-overlay/Xbox" / name, destination / "Xbox" / name)
    font = destination / "native/ext/stb_truetype"
    font.mkdir(parents=True, exist_ok=True)
    for name in ("stb_truetype.h", "LICENSE"):
        shutil.copyfile(project / "vendor/stb" / name, font / name)
    (destination / "git-version.cpp").write_text(
        '// Generated baseline provenance, not a release version.\n'
        '#define PPSSPP_GIT_VERSION_NO_UPDATE 1\n'
        'const char *PPSSPP_GIT_VERSION = "legacy-540db97-owner-6dd3c4f-m3";\n', encoding="utf-8")


def prepare(legacy, overlay, destination, compatibility=False):
    if compatibility:
        destination.relative_to(Path(__file__).resolve().parents[1])
    report = verify_overlay(overlay)
    if report["status"] != "PASS":
        raise ValueError("Owner source failed verification; staging was not created")
    git = ["git", "-c", "safe.directory=" + legacy.as_posix(), "-C", str(legacy)]
    actual = subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()
    if actual != LEGACY_COMMIT:
        raise ValueError("Legacy checkout is not at the pinned commit")
    if destination.exists():
        raise ValueError("Destination already exists; preserve it and select a fresh directory")
    # Read committed donor objects, excluding generated/untracked local build files.
    donor = subprocess.check_output(git + ["archive", "--format=zip", LEGACY_COMMIT])
    owner = base64.b64decode(b"".join(b"".join((overlay / name).read_bytes().split()) for name in PART_NAMES), validate=True)
    manifest = {}
    destination.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(donor)) as archive:
        unpack(archive, destination, manifest, "legacy@" + LEGACY_COMMIT)
    with zipfile.ZipFile(io.BytesIO(owner)) as archive:
        unpack(archive, destination, manifest, "verified-owner-overlay")
    receipt = {"schema_version": 1, "legacy_commit": actual,
               "owner_archive_sha256": report["actual_sha256"], "files": manifest}
    (destination / "BASELINE_SOURCE_MANIFEST.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if compatibility:
        apply_build_compatibility(destination, Path(__file__).resolve().parents[1])
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--overlay", type=Path, default=Path(__file__).resolve().parents[1] / "source-overlay")
    parser.add_argument("--with-build-compatibility", action="store_true",
                        help="Apply recorded local-only build and launcher compatibility patches")
    args = parser.parse_args()
    receipt = prepare(args.legacy.resolve(), args.overlay.resolve(), args.destination.resolve(),
                      args.with_build_compatibility)
    print(json.dumps({"status": "PASS", "files": len(receipt["files"]),
                      "legacy_commit": receipt["legacy_commit"],
                      "owner_archive_sha256": receipt["owner_archive_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
