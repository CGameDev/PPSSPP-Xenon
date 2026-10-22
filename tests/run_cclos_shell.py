#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Enforce the approved shell's narrow source boundary against its exact M5 input."""
import argparse
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from run_cclos_launcher import function

ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ('RenderCclosBackground', 'RenderTabBar', 'RenderListItem',
                'RenderGameList', 'RenderGridItem', 'RenderGrid',
                'RenderRightPanel', 'RenderInGameMenu')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', required=True, type=Path)
    p.add_argument('--build-root', required=True, type=Path)
    args = p.parse_args()
    build = args.build_root.resolve()
    build.relative_to(ROOT / 'artifacts')
    reference = build / 'previous/Xbox/XboxLauncher.cpp'
    reference.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.source_root / 'Xbox/XboxLauncher.cpp', reference)
    subprocess.run(['git', '-C', str(ROOT), 'apply', '-R',
                    '--directory=' + reference.parents[1].relative_to(ROOT).as_posix(),
                    str(ROOT / 'baseline-overlay/cclos-approved-shell.patch')], check=True)
    current = (args.source_root / 'Xbox/XboxLauncher.cpp').read_text(encoding='latin1')
    previous = reference.read_text(encoding='latin1')
    for name in ('UpdateInGameMenu', 'ShowToast', 'RenderToast', 'DrawFittedString', 'DrawFittedTexture'):
        assert function(current, name) == function(previous, name), name
    for name in PRESENTATION:
        assert function(current, name) != function(previous, name), name
        # Six replacement bodies add one separating newline; the two retained
        # loops change only coordinates and preserve their original whitespace.
        suffix = '' if name in ('RenderGameList', 'RenderGrid') else '\n'
        current = current.replace(function(current, name) + suffix, '// presentation: ' + name)
        previous = previous.replace(function(previous, name), '// presentation: ' + name)
    current = current.replace('#include "CclosShellLayout.h"\n', '')
    current = current.replace('COL_LEFT_X = 240;', 'COL_LEFT_X = SAFE_X;')
    current = current.replace('COL_LEFT_W = 704;', 'COL_LEFT_W = 780;')
    for name in ('ContentHeight', 'GridWidth', 'GridHeight', 'Columns', 'Rows', 'ListHeight', 'OffsetForSelection'):
        current = current.replace('CclosShell::' + name, 'CclosLauncher::' + name)
    assert current == previous, 'Change escaped the presentation/geometry boundary:\n' + ''.join(
        difflib.unified_diff(previous.splitlines(True), current.splitlines(True)))
    result = {'status': 'PASS', 'changed_presentation_methods': list(PRESENTATION),
              'other_cpp_source': 'Exact M5 equality after explicit include/geometry substitutions',
              'unchanged_methods': ['UpdateInGameMenu', 'ShowToast', 'RenderToast', 'DrawFittedString', 'DrawFittedTexture'],
              'xbox_runtime': 'NOT RUN'}
    (build / 'RECEIPT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
