#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Check the actual PGF reader against a bit oracle and all pinned font tables."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from run_m3_regressions import function

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',required=True,type=Path)
    p.add_argument('--build-root',required=True,type=Path)
    args=p.parse_args()
    source=args.source_root.resolve();build=args.build_root.resolve()
    build.relative_to(ROOT/'artifacts');build.mkdir(parents=True,exist_ok=True)
    reference=build/'reference/Core/Font/PGF.cpp';reference.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source/'Core/Font/PGF.cpp',reference)
    subprocess.run(['git','-C',str(ROOT),'apply','-R','--directory='+reference.parents[2].relative_to(ROOT).as_posix(),str(ROOT/'baseline-overlay/pgf-endian-fix.patch')],check=True)
    current=(source/'Core/Font/PGF.cpp').read_text(encoding='latin1')
    old=reference.read_text(encoding='latin1')
    new_reader=function(current,r'static int getBits\(')
    old_reader=function(old,r'static int getBits\(')
    assert current.replace(new_reader,'// bit reader')==old.replace(old_reader,'// bit reader')
    (build/'pgf_current.inc').write_text(new_reader.replace('getBits(', 'currentGetBits('))
    # Only the test's word-loading type changes to emulate a native BE host.
    negative=old_reader.replace('getBits(', 'oldBigEndianGetBits(').replace('const u32 *wordbuf = (const u32 *)buf;', 'const BigWord *wordbuf = (const BigWord *)buf;')
    (build/'pgf_old_be.inc').write_text(negative)
    compiler=shutil.which('g++') or shutil.which('cl')
    if not compiler:raise RuntimeError('Host compiler required')
    exe=build/'pgf-reader.exe'
    fixture=ROOT/'tests/pgf_reader_cases.cpp'
    if Path(compiler).stem.lower()=='cl':
        # Match production /W3; /WX remains strict for the extracted methods.
        command=[compiler,'/nologo','/EHsc','/W3','/WX','/I'+str(build),'/Fe'+str(exe),str(fixture)]
    else:
        command=[compiler,'-std=c++11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(build),str(fixture),'-o',str(exe)]
    result=subprocess.run(command,cwd=build,capture_output=True,text=True)
    (build/'compile.txt').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    fonts=sorted((source/'flash0/font').glob('*.pgf'));assert len(fonts)==18
    result=subprocess.run([str(exe)]+[str(f) for f in fonts],capture_output=True,text=True)
    (build/'run.txt').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr+'exit='+str(result.returncode))
    trace=json.loads(result.stdout)
    for path,item in zip(fonts,trace['fonts']):
        item.update(font=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    receipt=dict(status='PASS',source_sha256=hashlib.sha256((source/'Core/Font/PGF.cpp').read_bytes()).hexdigest(),
                 scope='Only getBits body differs from M6',actual_reader_checks=trace,
                 emulation='Explicit LE/BE word decoding on host; no PPC machine code executed',
                 xbox_runtime='NOT RUN; owner M6 launch previously failed')
    (build/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
