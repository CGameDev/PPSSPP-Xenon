# SPDX-License-Identifier: GPL-2.0-or-later
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_build_warnings import audit


class WarningAuditTests(unittest.TestCase):
    def test_summary_duplicates_are_not_counted_twice(self):
        result = audit("LINK : warning C4742: alignment\nx.cpp(1): warning C4715: return\n"
                       "Build succeeded.\nLINK : warning C4742: alignment\n")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["by_code"], {"C4715": 1, "C4742": 1})


class LocalBuildSafetyTests(unittest.TestCase):
    def test_unsafe_deployment_metadata_refused_before_build(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Xbox/xx").mkdir(parents=True)
            for entry in ("", "<Deploy />", "<Deploy><ExcludedFromBuild>false</ExcludedFromBuild></Deploy>"):
                with self.subTest(entry=entry):
                    (root / "Xbox/xx/xx.vcxproj").write_text(
                        '<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'
                        '<ItemDefinitionGroup>' + entry + '</ItemDefinitionGroup></Project>')
                    result = subprocess.run([shell, "-NoProfile", "-File",
                                             str(ROOT / "tools/build_baseline.ps1"),
                                             "-SourceRoot", str(root), "-Rebuild"],
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    # PowerShell 7 on Linux adds ANSI styling and wraps long error text.
                    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
                    output = " ".join(output.split())
                    self.assertTrue("deployment metadata is missing" in output or
                                    "Local-only build refused" in output, output)
                    self.assertFalse((root / "build-Debug.log").exists())
