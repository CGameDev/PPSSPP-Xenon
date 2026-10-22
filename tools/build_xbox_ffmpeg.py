#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the pinned donor's Xbox FFmpeg recipe using local licensed XDK tools."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

from verify_xbox_libraries import LIBRARIES, verify


def recipe_arguments(source, configuration):
    debug = configuration == "Debug"
    recipe = (source / ("xbox.360.build.d.sh" if debug else "xbox.360.build.sh")).read_text()
    prefix = source / "Xbox" / ("ppcD" if debug else "ppc")
    args = []
    for key in ("GENERAL", "AUDIO_DECODERS", "VIDEO_DECODERS", "BSFS", "PARSERS",
                "DEMUXERS", "HARDWARE_ACCELS", "INPUT_DEVICES"):
        block = re.search(r"^" + key + r'="(.*?)^"', recipe, re.S | re.M).group(1)
        for line in block.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                args.append(line.replace("${ARCH}", "ppc").replace("$PREFIX", prefix.as_posix()))
    args += ["--enable-static", "--disable-shared", "--host-cc=cl"]
    flags = ("-MTd" if debug else "-MT") + " -I" + (source / "XboxInclude").as_posix()
    if not debug:
        flags += " -Ox -Ot"
    args += ["--extra-cflags=" + flags,
             "--extra-ldflags=" + ("-DEBUG xapilibd.lib xboxkrnl.lib vcompd.lib xbdm.lib"
                                    if debug else "xapilib.lib xboxkrnl.lib vcomp.lib")]
    return args, prefix


def short_path(path):
    buffer = ctypes.create_unicode_buffer(32768)
    if not ctypes.windll.kernel32.GetShortPathNameW(str(path), buffer, len(buffer)):
        raise ValueError("Cannot resolve the existing Bash executable's short path")
    return buffer.value.replace("\\", "/")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "build", "make", "c99", "xdk", "bash"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--configuration", choices=("Debug", "Release"), required=True)
    parser.add_argument("--resume", action="store_true",
                        help="Reuse an existing configuration only if its arguments match exactly")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This XDK driver requires Windows")
    source, build = args.source.resolve(), args.build.resolve()
    xdk, bash, make, c99 = (getattr(args, name).resolve() for name in ("xdk", "bash", "make", "c99"))
    if " " in str(source) or " " in str(build):
        parser.error("The historical FFmpeg Makefiles require source/build paths without spaces")
    for path in (source / "configure", xdk / "bin/win32/cl.exe", xdk / "bin/win32/link.exe",
                 bash, make, c99 / "c99wrap.exe", c99 / "c99conv.exe"):
        if not path.is_file():
            parser.error("Missing local dependency: " + str(path))
    manifest = json.loads((source.parent / "BASELINE_SOURCE_MANIFEST.json").read_text())
    if manifest["legacy_commit"] != "540db97d96136b2139e5f12dd3c0bb18f2e1cd1f":
        parser.error("Unexpected legacy source identity")
    for name, item in manifest["files"].items():
        if name.startswith("ffmpeg/"):
            if hashlib.sha256((source.parent / name).read_bytes()).hexdigest() != item["sha256"]:
                parser.error("Pinned FFmpeg source was modified: " + name)
    configure, prefix = recipe_arguments(source, args.configuration)
    if build.exists() and not args.resume:
        parser.error("Build directory exists; use a fresh directory or validated --resume")
    build.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["INCLUDE"] = str(xdk / "include/xbox") + ";" + str(xdk / "include/xbox/sys")
    env["LIB"] = str(xdk / "lib/xbox")
    env["PATH"] = str(xdk / "bin/win32") + ";" + env["PATH"]

    def posix(path):
        return subprocess.check_output([str(bash), "--noprofile", "--norc", "-c",
                                        "cygpath -u " + shlex.quote(path.as_posix())],
                                       env=env, text=True).strip()

    preamble = ('#!/bin/bash\nset -euo pipefail\nexport PATH=' +
                shlex.quote(posix(xdk / "bin/win32") + ":" + posix(c99)) +
                ':"$PATH"\ncd ' + shlex.quote(build.as_posix()) + "\n")

    def run_script(name, command):
        script = build / (name + ".sh")
        with script.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(preamble + command + "\n")
        with (build / (name + ".log")).open("wb") as log:
            subprocess.run([str(bash), "--noprofile", "--norc", str(script)], env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)

    if args.resume:
        header = (build / "config.h").read_text()
        actual = re.search(r'^#define FFMPEG_CONFIGURATION "(.*)"$', header, re.M).group(1)
        if shlex.split(actual) != configure:
            parser.error("Existing FFmpeg configuration differs from the pinned recipe")
    else:
        run_script("configure", "bash " + shlex.quote((source / "configure").as_posix()) +
                   " " + " ".join(map(shlex.quote, configure)))
    header = (build / "config.h").read_text()
    if ("#define ARCH_PPC 1" not in header or "#define ARCH_PPC64 0" not in header
            or "#define HAVE_BIGENDIAN 1" not in header):
        parser.error("Configuration is not 32-bit big-endian PowerPC")
    # Native GNU Make reads Windows paths; Git Bash configure emits /c/... paths.
    for name in ("config.mak", "Makefile"):
        path = build / name
        content = path.read_text().replace(posix(source), source.as_posix())
        with path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    # The old MSVC dependency-scanner pipeline is incompatible with native Make/
    # modern Git Bash quoting. Build fresh trees; header changes require a fresh
    # rebuild. No codec source, compiler optimization or feature is changed.
    run_script("make", shlex.quote(make.as_posix()) + " " +
               shlex.quote("SHELL=" + short_path(bash)) +
               " CCDEP=echo ASDEP=echo HOSTCCDEP=echo -j3 all")
    library_dir = prefix / "lib"
    library_dir.mkdir(parents=True, exist_ok=True)
    for name in LIBRARIES:
        archive = build / ("lib" + name) / ("lib" + name + ".a")
        (library_dir / (name + ".lib")).write_bytes(archive.read_bytes())
    report = verify(library_dir)
    report["configuration"] = args.configuration
    report["configure_arguments"] = configure
    with (build / "BUILD_RECEIPT.json").open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
