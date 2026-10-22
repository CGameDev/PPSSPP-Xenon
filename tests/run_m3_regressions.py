#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Run host regression cases extracted from the actual assembled source."""
import argparse
import base64
import hashlib
import json
import io
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def function(source, pattern):
    start = re.search(pattern, source).start()
    brace = source.index("{", start)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    args = parser.parse_args()
    source, build = args.source_root.resolve(), args.build_root.resolve()
    build.relative_to(ROOT / "artifacts")
    build.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("cl")
    if not compiler:
        raise SystemExit("A host compiler is required; do not skip these checks")
    msvc = Path(compiler).stem.lower() == "cl"
    records = []

    def read(name):
        data = (source / name).read_bytes()
        records.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
        return data.decode("latin1").replace("\r\n", "\n")

    def generated(name, content):
        (build / name).write_bytes(content.encode("latin1"))

    def run(name, fixture, includes=(), strict=True, defines=(), quiet=False, warning_level=4):
        exe = build / (name + ".exe")
        if msvc:
            command = [compiler, "/nologo", "/EHsc", "/W" + str(warning_level), "/I" + str(build)]
            if strict:
                command.append("/WX")
            command += ["/I" + str(p) for p in includes]
            command += ["/D" + item for item in defines]
            command += ["/Fe" + str(exe), str(ROOT / "tests" / fixture)]
        else:
            command = [compiler, "-std=c++11", "-Wall", "-Wextra", "-I" + str(build)]
            if strict:
                command.append("-Werror")
            command += ["-I" + str(p) for p in includes]
            command += ["-D" + item for item in defines]
            command += [str(ROOT / "tests" / fixture), "-o", str(exe)]
        result = subprocess.run(command, cwd=build, capture_output=True, text=True)
        (build / (name + "-compile.log")).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        result = subprocess.run([str(exe)], cwd=build, capture_output=True, text=True, check=True)
        (build / (name + "-run.log")).write_text(result.stdout, encoding="utf-8")
        if not quiet:
            print(result.stdout.strip())
        return result.stdout

    vertex = read("GPU/Directx9/VertexDecoderDX9.cpp")
    generated("morph_function.inc", function(vertex, r"void VertexDecoderDX9::Step_NormalS16Morph\(\) const"))
    predicates = []
    for name, path, expr in [
        ("moduleArgs", "Core/HLE/sceKernelModule.cpp", "param.args > 0U"),
        ("startPriority", "Core/HLE/sceKernelModule.cpp", "module->nm.module_start_thread_priority > 0U"),
        ("startStack", "Core/HLE/sceKernelModule.cpp", "module->nm.module_start_thread_stacksize > 0U"),
        ("optionStack", "Core/HLE/sceKernelModule.cpp", "smoption.stacksize > 0U"),
        ("atracEnd", "Core/HLE/sceAtrac.cpp", "context->info.endSample > 0U"),
        ("secureEntries", "Core/Dialog/SavedataParam.cpp", "fileList->maxSecureEntries > 99U"),
        ("normalEntries", "Core/Dialog/SavedataParam.cpp", "fileList->maxNormalEntries > 8192U"),
        ("systemEntries", "Core/Dialog/SavedataParam.cpp", "fileList->maxSystemEntries > 5U")]:
        assert expr in read(path), expr
        test_expr = re.sub(r".* > ", "value > ", expr)
        predicates.append("static bool " + name + "(u32_le value) { return " + test_expr + "; }")
    generated("unsigned_predicates.inc", "\n".join(predicates))
    prefix = re.search(r"bool negate = [^;]+;", read("Core/MIPS/PPC/PpcCompVFPU.cpp")).group()
    generated("prefix_flag.inc", "static bool negateFlag(u32 prefix,int i) { " + prefix + " return negate; }")
    generated("tile_function.inc", function(read("GPU/Directx9/helper/global.cpp"), r"VOID LargestTileRectSize\("))
    launcher = read("Xbox/XboxLauncher.cpp")
    start = launcher.index("\t// Start at the game root")
    end = launcher.index("\n", launcher.index('currentDir_ = "game:', start))
    generated("root_initialization.inc", launcher[start:end] + "\n")
    run("numeric", "m3_numeric_cases.cpp", [source])
    run("session", "m3_session_cases.cpp", [source / "Xbox"])
    loop_header = read("Xbox/XenonEmulationLoop.h")
    owner = base64.b64decode(b"".join(b"".join(p.read_bytes().split()) for p in sorted((ROOT / "source-overlay").glob("*.b64"))), validate=True)
    with zipfile.ZipFile(io.BytesIO(owner)) as archive:
        original_main = archive.read("Xbox/XboxMain.cpp").decode("latin1").replace("\r\n", "\n")
    start = original_main.index("\t\tbool igmWasActive = false;")
    end = original_main.index("\n\n\t\tif (returnToMenu)", start)
    original_loop = original_main[start:end]
    moved = "\n".join(line[1:] if line.startswith("\t") else line for line in original_loop.split("\n"))
    moved = moved.replace("\t\tpspInited = false;", "\t\treturn false;")
    assert moved in loop_header
    call = "\t\tif (!RunEmulationSession(launcher, xbhost, returnToMenu, resetGame, exitToXbox)) {\n\t\t\tpspInited = false;\n\t\t}"
    expected_main = (original_main[:start] + call + original_main[end:]).replace(
        "\nint main(int argc, const char* argv[])", '\n#include "XenonEmulationLoop.h"\n\nint main(int argc, const char* argv[])')
    assert read("Xbox/XboxMain.cpp") == expected_main
    print("PASS: owner loop body, crash filter and surrounding lifecycle preserved by exact source comparison")

    reference = args.reference_root.resolve()
    old_vertex = (reference / "GPU/Directx9/VertexDecoderDX9.cpp").read_bytes().decode("latin1")
    generated("morph_function.inc", function(old_vertex, r"void VertexDecoderDX9::Step_NormalS16Morph\(\) const"))
    run("morph-negative", "m3_numeric_cases.cpp", [reference], strict=False, defines=["EXPECT_LEGACY_MORPH"])
    generated("morph_function.inc", function(vertex, r"void VertexDecoderDX9::Step_NormalS16Morph\(\) const"))

    emitter = read("Common/ppcEmitter.cpp")
    methods = ["MFLR", "MTLR", "LI", "LIS", "ORI", "MOVI2R", "ADDI", "STW", "STWU", "LD", "STD", "LWZ", "LFD", "SFD", "Prologue", "Epilogue"]
    outputs = []
    for label, text in [("reference", (reference / "Common/ppcEmitter.cpp").read_bytes().decode("latin1").replace("\r\n", "\n")),
                        ("current", emitter)]:
        macros = text[text.index("#define X_FORM"):text.index("namespace PpcGen")]
        bodies = [function(text, r"void\s+PPCXEmitter::" + name + r"\s*\(") for name in methods]
        # Normalize the address of this shared scratch buffer for host comparison only.
        content = macros + "\n" + "\n".join(bodies).replace("(u32)&_fprTmp", "0x12345678U")
        generated("emitter_functions.inc", content)
        # Use the real emitter project's /W3; unchanged primitives have /W4 narrowing diagnostics.
        outputs.append(run("emitter-" + label, "m3_emitter_cases.cpp", strict=label == "current", quiet=True, warning_level=3))
    assert outputs[0] == outputs[1]
    print("PASS: all 82 emitted PPC prologue/epilogue words match reference (scratch address normalized)")

    cache_header = read("Core/MIPS/JitCommon/JitBlockCache.h")
    generated("cache_init_method.inc", function(cache_header, r"void Init\(CodeBlock \*codeBlock\)"))
    generated("cache_constructor.inc", function(read("Core/MIPS/JitCommon/JitBlockCache.cpp"), r"JitBlockCache::JitBlockCache\("))
    generated("jit_constructor.inc", function(read("Core/MIPS/PPC/PpcJit.cpp"), r"Jit::Jit\("))
    run("cache", "m3_cache_cases.cpp")

    hashes = []
    for label, path in [("reference", reference), ("current", source)]:
        hashes.append(run("hash-" + label, "m3_hash_cases.cpp", [path / "ext"], strict=label == "current", quiet=True))
    assert hashes[0] == hashes[1]
    read("ext/xxhash.c")
    print("PASS: 32 xxHash outputs match reference, including streaming/chunk boundaries")
    macro = re.search(r"^#define XXH_STATIC_ASSERT[^\n]+", read("ext/xxhash.c"), re.M).group()
    generated("false_hash_assert.cpp", macro + "\nvoid invalid_size() { XXH_STATIC_ASSERT(0); }\n")
    command = ([compiler, "/nologo", "/c", str(build / "false_hash_assert.cpp")] if msvc else
               [compiler, "-std=c++11", "-c", str(build / "false_hash_assert.cpp")])
    rejected = subprocess.run(command, cwd=build, capture_output=True, text=True)
    assert rejected.returncode != 0
    (build / "false-assert-rejection.log").write_text(rejected.stdout + rejected.stderr, encoding="utf-8")
    print("PASS: false xxHash size assertion still fails compilation")
    receipt = {"status": "PASS", "host_compiler": Path(compiler).name,
               "native_host_seh": msvc, "xbox_execution": "NOT RUN", "source_files": records}
    (build / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
