#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Assemble a local, hash-checked smoke-test kit. No network, device or launch API."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CONFIGURATIONS = ('Release_LTCG', 'Debug')
CORE_ASSETS = ('Roboto-Condensed.ttf', 'ui_atlas.zim', 'unknown.png', 'ppge_atlas.zim')
DATA_DIRS = ('memstick/PSP/SAVEDATA', 'memstick/PSP/PPSSPP_STATE',
             'memstick/PSP/SYSTEM', 'memstick/PSP/GAME', 'memstick/PSP/SCREENSHOT', 'memstick/PAUTH')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_path(base, relative):
    path = base / relative
    path.resolve().relative_to(base.resolve())
    if path.is_symlink():
        raise ValueError('Symlink input refused: ' + str(path))
    return path


def validate_source(stage, receipts):
    manifest = json.loads((stage / 'BASELINE_SOURCE_MANIFEST.json').read_text())
    if manifest['legacy_commit'] != '540db97d96136b2139e5f12dd3c0bb18f2e1cd1f':
        raise ValueError('Unexpected donor identity')
    if manifest['owner_archive_sha256'] != '6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35':
        raise ValueError('Unexpected owner archive identity')
    for name in CORE_ASSETS:
        if not (stage / 'assets' / name).is_file():
            raise ValueError('Missing runtime asset: ' + name)
    if len(list((stage / 'flash0/font').glob('*.pgf'))) != 18:
        raise ValueError('Expected the pinned 18 bundled flash0 fonts')
    runtime = []
    for directory in ('assets', 'flash0', 'lang'):
        for path in sorted((stage / directory).rglob('*')):
            if path.is_file():
                relative = path.relative_to(stage).as_posix()
                safe_path(stage, relative)
                if sha(path) != manifest['files'][relative]['sha256']:
                    raise ValueError('Runtime bytes differ from source manifest: ' + relative)
                runtime.append(relative)
    by_config = {item['configuration']: item for item in receipts}
    for configuration in CONFIGURATIONS:
        record = by_config[configuration]
        xex = stage / f'Xbox/xx/{configuration}/xx.xex'
        with xex.open('rb') as stream:
            magic = stream.read(4)
        if (magic != b'XEX2' or sha(xex) != record['sha256']
                or xex.stat().st_size != record['bytes']
                or record['warnings'] != 0 or record['errors'] != 0):
            raise ValueError('Candidate XEX identity/build gate failed: ' + configuration)
    return runtime


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def verify_kit(destination):
    manifest = json.loads((destination / 'MANIFEST.json').read_text())
    for record in manifest['files']:
        path = safe_path(destination, record['path'])
        if not path.is_file() or path.stat().st_size != record['bytes'] or sha(path) != record['sha256']:
            raise ValueError('Kit hash/size mismatch: ' + record['path'])
    for relative in manifest['required_directories']:
        if not safe_path(destination, relative).is_dir():
            raise ValueError('Missing kit directory: ' + relative)
    return len(manifest['files'])


def prepare(destination, candidate, rollback):
    destination = destination.resolve()
    archive = destination.with_suffix('.zip')
    if destination.exists() or archive.exists():
        raise ValueError('Fresh destination and ZIP required; existing files are preserved')
    groups = []
    for milestone, stage, parent in [('m6', candidate, 'candidate'), ('m5', rollback, 'rollback')]:
        receipts = json.loads((ROOT / f'docs/evidence/{milestone}/baseline-builds.json').read_text())
        runtime = validate_source(stage, receipts)
        groups.append((milestone, stage, parent, receipts, runtime))
    # Validate every input before creating a destination; never repair/replace sources.
    destination.mkdir(parents=True)
    apps, required_dirs = [], []
    for milestone, stage, parent, receipts, runtime in groups:
        for configuration in CONFIGURATIONS:
            app = Path(parent) / (configuration if milestone == 'm6' else 'M5-' + configuration)
            copy_file(stage / f'Xbox/xx/{configuration}/xx.xex', destination / app / 'xx.xex')
            for name in runtime:
                copy_file(stage / name, destination / app / name)
            for name in DATA_DIRS:
                relative = (app / name).as_posix()
                (destination / relative).mkdir(parents=True)
                required_dirs.append(relative)
            record = next(x for x in receipts if x['configuration'] == configuration)
            apps.append(dict(path=app.as_posix(), milestone=milestone, configuration=configuration,
                             xex_sha256=record['sha256'], runtime_files=len(runtime),
                             xbox_runtime='NOT RUN'))
    for name in ('START-HERE.md', 'CHECKLIST.md', 'ROLLBACK.md', 'VERIFY-LOCAL.py', 'VERIFY-LOCAL.ps1'):
        copy_file(ROOT / 'docs/smoke-test' / name, destination / name)
    for milestone in ('m6', 'm5'):
        for name in ('baseline-builds.json',):
            copy_file(ROOT / f'docs/evidence/{milestone}' / name, destination / f'evidence/{milestone}' / name)
    for name in ('debug-rebuild.txt', 'release-ltcg-rebuild.txt', 'launcher-receipt.json',
                 'ingame-receipt.json', 'shell-boundary.json', 'ffmpeg-libraries.json'):
        copy_file(ROOT / 'docs/evidence/m6' / name, destination / 'evidence/m6' / name)
    copy_file(ROOT / 'docs/BASELINE.md', destination / 'evidence/M6-BASELINE.md')
    for relative in ('LICENSE', 'LICENSE.TXT', 'ffmpeg/LICENSE', 'ffmpeg/COPYING.GPLv2',
                     'ffmpeg/COPYING.LGPLv2.1', 'ffmpeg/COPYING.LGPLv3',
                     'native/LICENSE.TXT', 'native/ext/stb_truetype/LICENSE',
                     'native/ext/cityhash/COPYING', 'ext/snappy/COPYING'):
        copy_file(candidate / relative, destination / 'licenses' / relative)
    results = destination / 'results'
    results.mkdir()
    environment = dict(candidate_source_commit='6657e9f0b0935fa108fb55eab72d151ed4a5a34c',
                       candidate_configuration='Release_LTCG', console='NOT CONFIRMED',
                       loader='NOT CONFIRMED', output_mode='NOT CONFIRMED',
                       intended_test_folder='NOT CONFIRMED', original_install_path='NOT CONFIRMED',
                       backup_path='NOT CONFIRMED', backup_verified=False,
                       iso=dict(available=True, title='NOT RECORDED', bytes=None, sha256=None,
                                inspected_by_agent=False),
                       console_transfer_authorized=False, console_launch_authorized=False,
                       actual_backend='NOT OBSERVED', frame_time_measurements='NOT MEASURED',
                       console_results='NOT RUN')
    (results / 'environment.json').write_text(json.dumps(environment, indent=2) + '\n')
    for name, rows in [('checklist.csv',
                       [[f'{prefix}{i:02}', 'NOT RUN', '', ''] for prefix, count in [('P', 5), ('S', 14), ('E', 5)] for i in range(1, count + 1)]),
                      ('transitions.csv', [[str(i), 'NOT RUN', '', ''] for i in range(1, 21)])]:
        with (results / name).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'result', 'observation_or_transition', 'evidence_filename'])
            writer.writerows(rows)
    (destination / 'evidence/SOURCE-PROVENANCE.json').write_text(json.dumps(dict(
        candidate_commit='6657e9f0b0935fa108fb55eab72d151ed4a5a34c',
        rollback_checkpoint='M5 / b82bad8848956e55d04933bfb04e9019f9b6ecb0',
        source_repository='https://github.com/CGameDev/PPSSPP-Xenon',
        preparation='tools/prepare_baseline.py plus recorded build procedures; no executable modified',
        donor_commit='540db97d96136b2139e5f12dd3c0bb18f2e1cd1f',
        original_overlay_sha256='6dd3c4f3c21bc6d5603861ee3f8a0b5b4a480e6218fbbbe95c87ecd7bd090e35',
        console_actions='NONE', user_iso='Not included or inspected'), indent=2) + '\n')
    files = [dict(path=p.relative_to(destination).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
             for p in sorted(destination.rglob('*'))
             if p.is_file() and p.relative_to(destination).parts[0] != 'results']
    manifest = dict(schema_version=1, status='PREPARED LOCALLY / XBOX NOT RUN',
                    apps=apps, required_directories=required_dirs, files=files,
                    editable_results=['results/environment.json', 'results/checklist.csv', 'results/transitions.csv'],
                    optional_missing=['assets/splash.png'], console_actions='NONE', iso_included=False)
    (destination / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (destination / 'SHA256SUMS.txt').write_text(''.join(x['sha256'] + '  ' + x['path'] + '\n' for x in files))
    count = verify_kit(destination)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(destination.rglob('*')):
            z.write(path, path.relative_to(destination).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    return dict(status='PASS', files_verified=count, applications=4, zip=str(archive),
                zip_bytes=archive.stat().st_size, zip_sha256=sha(archive), xbox_actions='NONE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=ROOT / 'artifacts/baseline-m6')
    parser.add_argument('--rollback', type=Path, default=ROOT / 'artifacts/baseline-m5')
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.destination, args.candidate.resolve(), args.rollback.resolve()), indent=2))
