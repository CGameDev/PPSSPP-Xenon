# SPDX-License-Identifier: GPL-2.0-or-later
"""Compile and exercise real owner functions with host-only failure injection."""
import base64
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class LauncherTextureTests(unittest.TestCase):
    def test_failure_cleanup_and_pixel_copy(self):
        compiler = shutil.which("g++") or shutil.which("cl")
        if not compiler:
            self.skipTest("Run with g++ or a Visual Studio host developer environment")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_bytes = base64.b64decode(b"".join(
                b"".join(p.read_bytes().split()) for p in sorted((ROOT / "source-overlay").glob("*.b64"))),
                validate=True)
            with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
                source = archive.read("Xbox/XboxLauncher.cpp").replace(b"\r\n", b"\n")
            (root / "Xbox").mkdir()
            launcher = root / "Xbox/XboxLauncher.cpp"
            launcher.write_bytes(source)
            for name in ("launcher-legacy-compat.patch", "warning-fixes.patch"):
                subprocess.run(["git", "apply", "--include=Xbox/XboxLauncher.cpp",
                                str(ROOT / "baseline-overlay" / name)], cwd=root, check=True)
            source = launcher.read_text(encoding="utf-8")
            functions = []
            for name in ("LoadGameIcon", "LoadPNGTexture"):
                start = source.index("IDirect3DTexture9 *XboxLauncher::" + name + "(")
                end = source.index("\n}\n", start) + 3
                functions.append(source[start:end])
            (root / "launcher_texture_functions.inc").write_text("\n".join(functions), encoding="utf-8")
            exe = root / "texture-cases.exe"
            fixture = ROOT / "tests/launcher_texture_cases.cpp"
            if Path(compiler).stem.lower() == "cl":
                command = [compiler, "/nologo", "/EHsc", "/W4", "/WX", "/I" + str(root),
                           "/Fe" + str(exe), str(fixture)]
            else:
                command = [compiler, "-std=c++98", "-Wall", "-Wextra", "-Werror", "-pedantic",
                           "-I" + str(root), str(fixture), "-o", str(exe)]
            subprocess.run(command, cwd=root, check=True)
            subprocess.run([str(exe)], cwd=root, check=True)


if __name__ == "__main__":
    unittest.main()
