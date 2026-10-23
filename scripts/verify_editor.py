"""Verify the freshly extracted portable editor without bundling private inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from patcher_core import TARGET_SHA256

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    args = parser.parse_args()
    original_hash = hashlib.sha256(args.original.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='cornell-portable-') as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(ROOT / 'dist/Text-Tool-V0.6.zip') as z:
            assert z.testzip() is None
            assert not any('/work/' in n or n.lower().endswith(('.z64', '.n64', '.v64', '.dll', '.srm')) for n in z.namelist())
            z.extractall(folder)
        editor = folder / '묵시록외전_텍스트도구'
        assert not (editor / 'work').exists()
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        subprocess.run([sys.executable, str(editor / 'tools/prepare_project.py'), str(args.original.resolve())],
                       check=True, timeout=90, capture_output=True, creationflags=flags)
        for flag in ['--self-check', '--build-check']:
            subprocess.run([str(editor / 'Cornell_Korean_Editor.exe'), flag],
                           check=True, timeout=120, capture_output=True, creationflags=flags)
        ui = json.loads((editor / 'editor-self-check.json').read_text(encoding='utf-8'))
        build = json.loads((editor / 'build-self-check.json').read_text(encoding='utf-8'))
        assert ui['rows'] == 1665 and ui['stats']['pending'] == 0
        assert build['sha256'] == TARGET_SHA256
        assert hashlib.sha256((editor / 'work/korean-candidate.z64').read_bytes()).hexdigest() == TARGET_SHA256
    assert hashlib.sha256(args.original.read_bytes()).hexdigest() == original_hash
    result = dict(success=True, freshly_extracted_archive_verified=True, archive_contains_no_rom_or_work=True,
                  standalone_editor_gui_verified=True, translated_rows=1665,
                  standalone_editor_rebuilt_same_target=True, target_sha256=TARGET_SHA256,
                  original_preserved=True)
    (ROOT / 'dist/editor-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
