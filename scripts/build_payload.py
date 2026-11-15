"""Reproduce the included BPS from separately supplied original and target ROMs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bps import create
from patcher_core import normalize, SOURCE_SHA1, SOURCE_SHA256, TARGET_SHA256

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    source = normalize(args.original.read_bytes())
    target = args.target.read_bytes()
    assert hashlib.sha1(source).hexdigest() == SOURCE_SHA1
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256
    assert hashlib.sha256(target).hexdigest() == TARGET_SHA256
    metadata = dict(game='Akumajou Dracula Mokushiroku Gaiden - Legend of Cornell (Japan)',
                    version='v0.65', language='ko', target_sha256=TARGET_SHA256)
    patch = create(source, target, json.dumps(metadata, ensure_ascii=False).encode())
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(patch).hexdigest() == manifest['patch_sha256']
    output = ROOT / 'data' / manifest['patch_file']
    output.write_bytes(patch)
    print(output.name, manifest['patch_sha256'])

if __name__ == '__main__':
    main()
