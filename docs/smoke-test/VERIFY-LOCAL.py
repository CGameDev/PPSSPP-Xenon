#!/usr/bin/env python3
"""Read-only local kit verification; Python standard library, no device APIs."""
import hashlib
import json
from pathlib import Path


def verify(root):
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    if manifest['schema_version'] != 1:
        raise ValueError('Unsupported manifest version')
    for record in manifest['files']:
        path = (root / record['path']).resolve()
        path.relative_to(root.resolve())
        if not path.is_file() or path.stat().st_size != record['bytes']:
            raise ValueError('Size/type mismatch: ' + record['path'])
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        if h.hexdigest() != record['sha256']:
            raise ValueError('Hash mismatch: ' + record['path'])
    for relative in manifest['required_directories']:
        path = (root / relative).resolve()
        path.relative_to(root.resolve())
        if not path.is_dir():
            raise ValueError('Missing directory: ' + relative)
    return len(manifest['files']), len(manifest['required_directories'])


if __name__ == '__main__':
    files, directories = verify(Path(__file__).resolve().parent)
    print(f'PASS: {files} immutable packaged files and {directories} required directories.')
    print('Editable results, added ISO and generated data are not verified. No Xbox contacted or launched.')
