#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Compile actual launcher methods for host traces, input checks and UI previews."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def function(text, name):
    start = re.search(r"void XboxLauncher::" + name + r"\(", text).start()
    end = text.index("{", start) + 1
    depth = 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--reference-root", type=Path)
    p.add_argument("--build-root", type=Path, required=True)
    p.add_argument("--preview-data", type=Path)
    args = p.parse_args()
    build = args.build_root.resolve()
    build.relative_to(ROOT / "artifacts")
    build.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("cl")
    if not compiler:
        raise SystemExit("Host compiler required; do not skip launcher verification")
    msvc = Path(compiler).stem.lower() == "cl"
    if args.reference_root is None:
        # Recover just the immediately preceding launcher from this exact patch,
        # rather than relying on an untracked previous local build in CI.
        reference = build / "reference-source"
        for name in ("Xbox/XboxLauncher.cpp", "Xbox/XboxLauncher.h", "assets/Roboto-Condensed.ttf"):
            target = reference / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.source_root / name, target)
        approved_shell = 'CclosShellLayout.h' in (reference / 'Xbox/XboxLauncher.cpp').read_text(encoding='latin1')
        if approved_shell:
            subprocess.run(['git', '-C', str(ROOT), 'apply', '-R',
                            '--directory=' + reference.relative_to(ROOT).as_posix(),
                            str(ROOT / 'baseline-overlay/cclos-approved-shell.patch')], check=True)
        if not approved_shell and "Presentation only: existing input/state dispatch" in (reference / "Xbox/XboxLauncher.cpp").read_text(encoding="latin1"):
            subprocess.run(["git", "-C", str(ROOT), "apply", "-R",
                            "--directory=" + reference.relative_to(ROOT).as_posix(),
                            str(ROOT / "baseline-overlay/cclos-ingame-menu.patch")], check=True)
        if not approved_shell:
            subprocess.run(["git", "-C", str(ROOT), "apply", "-R",
                            "--directory=" + reference.relative_to(ROOT).as_posix(),
                            str(ROOT / "baseline-overlay/cclos-launcher-milestone.patch")], check=True)
        args.reference_root = reference
    records = []
    for label, root in [("current", args.source_root), ("reference", args.reference_root)]:
        if root is None:
            continue
        root = root.resolve()
        work = build / label
        work.mkdir(exist_ok=True)
        raw = (root / "Xbox/XboxLauncher.cpp").read_bytes()
        text = raw.decode("latin1").replace("\r\n", "\n")
        start = text.index("struct Margins {")
        end = text.index("static bool CompareGames", start)
        (work / "launcher_constants.inc").write_bytes(text[start:end].encode("latin1"))
        methods = ["RenderTabBar", "RenderListItem", "RenderGameList", "RenderGridItem", "RenderGrid",
                   "RenderRightPanel", "RenderAnimatedBackground", "Render", "RenderSplash", "Update"]
        if 'CclosLauncherTheme.h' in text:
            methods += ["RenderCclosBackground", "DrawFittedString", "DrawFittedTexture"]
        extracted = []
        for name in methods:
            body = function(text, name)
            if msvc and name == "RenderAnimatedBackground":
                # Preserved owner code, unused by the new launcher. Desktop MSVC
                # diagnoses its existing cos(double) conversion differently from XDK.
                body = '#pragma warning(push)\n#pragma warning(disable:4244)\n' + body + '\n#pragma warning(pop)\n'
            extracted.append(body)
        generated = "static const float DEADZONE = 0.3f;\n" + "\n".join(extracted)
        if 'CclosShellLayout.h' in text:
            generated = '#define CCLOS_APPROVED_SHELL 1\n' + generated
        elif 'CclosLauncherTheme.h' in text:
            generated = '#define CCLOS_PREVIOUS_SHELL 1\n' + generated
        (work / "launcher_methods.inc").write_bytes(generated.encode("latin1"))
        exe = work / "launcher-trace.exe"
        fixture = ROOT / "tests/cclos_launcher_trace.cpp"
        includes = [work, ROOT / "vendor/stb", ROOT / "baseline-overlay/Xbox"]
        if msvc:
            cmd = [compiler, "/nologo", "/EHsc", "/W3", "/D_CRT_SECURE_NO_WARNINGS"] + ["/I" + str(x) for x in includes]
            if label == "current": cmd += ["/WX"]
            if label == "reference": cmd += ["/DREFERENCE_RENDER"]
            cmd += ["/Fe" + str(exe), str(fixture)]
        else:
            cmd = [compiler, "-std=c++11", "-Wall", "-Wextra"] + ["-I" + str(x) for x in includes]
            # Keep diagnostics visible on the immutable historical reference.
            # Only the new implementation must pass with warnings as errors.
            if label == "current": cmd += ["-Werror"]
            if label == "reference": cmd += ["-DREFERENCE_RENDER"]
            cmd += [str(fixture), "-o", str(exe)]
        result = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
        (work / "compile.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        result = subprocess.run([str(exe), str(root / "assets/Roboto-Condensed.ttf")], cwd=work,
                                capture_output=True, text=True)
        (work / "run.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError("Launcher host assertions failed: " + result.stdout[-2000:] + result.stderr)
        frames = json.loads(result.stdout)
        (work / "trace.json").write_text(json.dumps(frames, indent=2) + "\n", encoding="utf-8")
        records.append({"label": label, "source_sha256": hashlib.sha256(raw).hexdigest(), "frames": frames})
    current = records[0]["frames"]
    assert all(x["animatedCalls"] == 0 for x in current)
    receipt = {"status": "PASS", "compiler": Path(compiler).name,
               "source_hashes": {x["label"]: x["source_sha256"] for x in records},
               "host_assertions": ["TV-safe actual packed-glyph quad bounds", "long/empty/missing-art/folder/loading/recent",
                                   "fitted text and image bounds", "RT debounce and selected-game visibility",
                                   "inactive renderer/input early return", "no scan/write/resource work while switching",
                                   "A file request/folder entry, LB/RB Recent policy and B exit with host stubs"],
               "font_sha256": hashlib.sha256((args.source_root / "assets/Roboto-Condensed.ttf").read_bytes()).hexdigest(),
               "console_execution": "NOT RUN", "budgets": []}
    if len(records) == 2:
        previous = records[1]['frames']
        if len(previous) == len(current):
            for a, b in zip(current, previous):
                assert (a['scene'], a['view']) == (b['scene'], b['view'])
                assert a['drawCalls'] <= b['drawCalls']
                assert a['cacheReads'] <= b['cacheReads']
                assert a['descReads'] <= b['descReads']
                # Different fitted captions use at most twelve additional glyphs.
                extra = 24 if a['scene'] == 'empty' else 6 if a['scene'] == 'folder' else 0
                assert a['triangles'] <= b['triangles'] + extra
            receipt['all_scene_cost_checks'] = len(current)
            receipt['extra_glyph_triangle_limits'] = {'empty': 24, 'folder': 6}
        for view in ("grid", "list"):
            a = next(x for x in current if x["scene"] == view)
            b = next(x for x in records[1]["frames"] if x["scene"] == view)
            assert a["drawCalls"] < b["drawCalls"]
            assert a["cacheReads"] <= b["cacheReads"]
            assert a["triangles"] < b["triangles"]
            receipt["budgets"].append({"view": view, "previous_draw_calls": b["drawCalls"], "current_draw_calls": a["drawCalls"],
                                       "previous_triangles": b["triangles"], "current_triangles": a["triangles"],
                                       "previous_cache_reads": b["cacheReads"], "current_cache_reads": a["cacheReads"],
                                       "previous_texture_descriptors": b["descReads"], "current_texture_descriptors": a["descReads"]})
    (build / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.preview_data:
        args.preview_data.write_text("window.CCLOS_FRAMES = " + json.dumps(current, separators=(",", ":")) + ";\n",
                                     encoding="utf-8", newline="\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
