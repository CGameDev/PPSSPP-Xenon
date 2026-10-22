#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Verify actual in-game presentation and unchanged owner actions on the host."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from run_cclos_launcher import function

ROOT = Path(__file__).resolve().parents[1]


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
    if args.reference_root is None:
        reference = build / "reference-source"
        for name in ("Xbox/XboxLauncher.cpp", "Xbox/XboxLauncher.h", "Core/SaveState.h", "assets/Roboto-Condensed.ttf"):
            target = reference / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.source_root / name, target)
        subprocess.run(["git", "-C", str(ROOT), "apply", "-R",
                        "--directory=" + reference.relative_to(ROOT).as_posix(),
                        str(ROOT / "baseline-overlay/cclos-ingame-menu.patch")], check=True)
        args.reference_root = reference
    compiler = shutil.which("g++") or shutil.which("cl")
    if not compiler:
        raise SystemExit("A host compiler is required; do not skip menu verification")
    msvc = Path(compiler).stem.lower() == "cl"
    records = []
    cpp_inputs = []
    state_inputs = []
    methods = ["RenderTabBar", "RenderListItem", "RenderGameList", "RenderGridItem", "RenderGrid",
               "RenderRightPanel", "RenderAnimatedBackground", "Render", "RenderSplash", "Update",
               "RenderCclosBackground", "DrawFittedString", "DrawFittedTexture",
               "UpdateInGameMenu", "ShowToast", "RenderToast", "RenderInGameMenu"]
    for label, root in [("current", args.source_root), ("reference", args.reference_root)]:
        root = root.resolve()
        work = build / label
        work.mkdir(exist_ok=True)
        raw = (root / "Xbox/XboxLauncher.cpp").read_bytes()
        text = raw.decode("latin1").replace("\r\n", "\n")
        cpp_inputs.append(text)
        header = (root / "Xbox/XboxLauncher.h").read_bytes().decode("latin1").replace("\r\n", "\n")
        setter = re.search(r"void SetInGameMenuActive\(bool active\) \{[^\n]+", header).group()
        state_inputs.append(setter)
        (work / "ingame_state.inc").write_bytes((setter + "\n").encode("latin1"))
        slots = re.search(r"const int SAVESTATESLOTS\s*=\s*\d+;", (root / "Core/SaveState.h").read_text()).group()
        assert re.search(r"=\s*5;", slots), "Requalify menu geometry if slot count changes"
        (work / "save_slots.inc").write_text(slots + "\n", encoding="utf-8")
        start = text.index("struct Margins {")
        end = text.index("static bool CompareGames", start)
        (work / "launcher_constants.inc").write_bytes(text[start:end].encode("latin1"))
        extracted = []
        for name in methods:
            body = function(text, name)
            if msvc and name == "RenderAnimatedBackground":
                body = '#pragma warning(push)\n#pragma warning(disable:4244)\n' + body + '\n#pragma warning(pop)\n'
            extracted.append(body)
        labels = re.search(r"static const char \*ingMenuLabelsR\[\][^\n]+", text).group()
        generated = "static const float DEADZONE = 0.3f;\n" + labels + "\n" + "\n".join(extracted)
        (work / "launcher_methods.inc").write_bytes(generated.encode("latin1"))
        includes = [work, ROOT / "vendor/stb", ROOT / "baseline-overlay/Xbox", ROOT / "tests"]
        exe = work / "ingame-trace.exe"
        if msvc:
            cmd = [compiler, "/nologo", "/EHsc", "/W3", "/D_CRT_SECURE_NO_WARNINGS"] + ["/I" + str(x) for x in includes]
            cmd += ["/WX"] if label == "current" else ["/DREFERENCE_RENDER"]
            cmd += ["/Fe" + str(exe), str(ROOT / "tests/cclos_ingame_trace.cpp")]
        else:
            cmd = [compiler, "-std=c++11", "-Wall", "-Wextra"] + ["-I" + str(x) for x in includes]
            cmd += ["-Werror"] if label == "current" else ["-DREFERENCE_RENDER"]
            cmd += [str(ROOT / "tests/cclos_ingame_trace.cpp"), "-o", str(exe)]
        result = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
        (work / "compile.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        result = subprocess.run([str(exe), str(root / "assets/Roboto-Condensed.ttf")], cwd=work, capture_output=True, text=True)
        (work / "run.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(result.stdout[-2000:] + result.stderr)
        trace = json.loads(result.stdout)
        (work / "trace.json").write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        records.append({"label": label, "sha256": hashlib.sha256(raw).hexdigest(), "trace": trace})
    for name in ("UpdateInGameMenu", "ShowToast"):
        assert function(cpp_inputs[0], name) == function(cpp_inputs[1], name), name
    assert state_inputs[0] == state_inputs[1]
    a, b = [x["trace"] for x in records]
    assert a["input_transcript"] == b["input_transcript"]
    budgets = []
    for current, reference in zip(a["frames"], b["frames"]):
        assert current["scene"] == reference["scene"]
        if current["scene"].startswith("menu-") and current["scene"] != "menu-no-atlas":
            assert current["drawCalls"] < reference["drawCalls"]
            assert current["triangles"] < reference["triangles"]
            assert current["animatedCalls"] == 0
        if current["scene"].startswith("toast-"):
            assert current["drawCalls"] <= reference["drawCalls"]
            # Fitting may replace one wide glyph with three narrow dots.
            # Count that bounded ellipsis work rather than claiming it is free.
            extra = 6 if current["scene"] == "toast-long" else 0
            assert current["triangles"] <= reference["triangles"] + extra
    for scene in ("menu-mixed", "menu-toast", "menu-no-atlas", "toast-0", "toast-long"):
        c = next(x for x in a["frames"] if x["scene"] == scene)
        r = next(x for x in b["frames"] if x["scene"] == scene)
        budgets.append({"scene": scene, "M4_draw_calls": r["drawCalls"], "M5_draw_calls": c["drawCalls"],
                        "M4_triangles": r["triangles"], "M5_triangles": c["triangles"]})
    receipt = {"status": "PASS", "compiler": Path(compiler).name,
               "source_hashes": {x["label"]: x["sha256"] for x in records},
               "frames": len(a["frames"]), "identical_action_snapshots": len(a["input_transcript"]),
               "unchanged_source": ["UpdateInGameMenu", "ShowToast", "SetInGameMenuActive"],
               "checks": ["all slots saved/empty, save/load/delete success/failure, held buttons", "all five session actions and cancel priority",
                          "panel navigation/clamping and request-flag reset", "toast 2000ms lifetime / final 500ms fade / long messages",
                          "packed glyph bounds, inactive no-work, five existing save-presence queries and no artwork/scans/writes"],
               "budgets": budgets, "xbox_execution": "NOT RUN"}
    (build / "RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if args.preview_data:
        args.preview_data.write_text("window.CCLOS_INGAME_FRAMES = " + json.dumps(a["frames"], separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
