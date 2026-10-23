"""Package only allowlisted patch, editor, documentation and screenshot files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from patcher_core import SOURCE_SHA1, SOURCE_SHA256, TARGET_SHA256

REPO = 'OldManCraveGuitars-bit/N64-Akumajou-Dracula-Mokushiroku-Gaiden-Legend-of-Cornell-Kr'
WEB = 'https://github.com/' + REPO
TAG = 'V0.6'
BASE = WEB + '/releases/download/' + TAG + '/'
EXE = 'N64-Legend-of-Cornell-Kr-V0.6-Patcher.exe'
PATCH = 'Legend-of-Cornell-Korean-V0.6.bps'
WINDOWS = 'N64-Legend-of-Cornell-Kr-V0.6-Windows.zip'
EDITOR = 'Text-Tool-V0.6.zip'
SCREENS = 'Screenshots-V0.6.zip'
RAW_HASH = 'c90e4e11e90a8688d655f59a3ad069814cfa24c2b55e5a959588b03dc4585a65'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
def jsonwrite(path, data): write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def archive(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, content in files:
            info = zipfile.ZipInfo(name, (2026, 10, 23, 0, 0, 0))
            z.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert not name.lower().endswith(('.z64', '.n64', '.v64', '.sav', '.srm', '.eep', '.state', '.dll'))
            assert '/work/' not in name and '/.qa/' not in name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--editor-exe', type=Path, required=True)
    args = parser.parse_args()
    dist = ROOT / 'dist'
    frozen = read(dist / 'patcher-verification.json')
    manifest = read(ROOT / 'data/manifest.json')
    assert frozen['all_passed'] and sha(dist / EXE) == frozen['executable_sha256']
    assert sha(ROOT / 'data' / PATCH) == manifest['patch_sha256']
    assert sha(ROOT / 'text-tool/work/korean-candidate.z64') == TARGET_SHA256
    verification = read(ROOT / 'docs/translation-validation.json')
    verification.pop('files', None)  # Private delivery filenames/hashes do not describe this release.
    verification['patch_bytes'] = (ROOT / 'data' / PATCH).stat().st_size
    verification['patcher'] = frozen
    verification['public_editor_source_rebuilt_same_target'] = True
    portable_report = dist / 'editor-verification.json'
    if portable_report.exists():
        portable = read(portable_report)
        assert portable['success'] and portable['target_sha256'] == TARGET_SHA256
        verification['public_portable_editor'] = portable
    jsonwrite(ROOT / 'docs/validation.json', verification)
    # Preserve the translation audit separately from the release-packaging results.
    old = read(ROOT / 'docs/translation-validation.json')
    old.pop('files', None)
    old['patch_bytes'] = verification['patch_bytes']
    jsonwrite(ROOT / 'docs/translation-validation.json', old)
    shutil.copy2(ROOT / 'data' / PATCH, dist / PATCH)
    rom_hashes = f'''악마성 드라큘라 묵시록 외전 / Legend of Cornell (Japan) · {TAG}

지원 원본: Akumajou Dracula Mokushiroku Gaiden - Legend of Cornell (Japan)
원본 크기: 16,777,216 bytes (16 MiB)
결과 크기: 33,554,432 bytes (32 MiB)

원본 SHA1 (big endian .z64 정규화): {SOURCE_SHA1}
원본 SHA256 (big endian .z64 정규화): {SOURCE_SHA256}
제공된 원본 SHA256 (v64 순서 / 확장자는 .n64): {RAW_HASH}
한국어 결과 SHA256 (.z64): {TARGET_SHA256}

확장자 대신 파일 헤더로 실제 바이트 순서를 판별합니다.
EXE는 .z64/.v64/.n64의 세 순서를 정규화하여 같은 원본인지 확인합니다.
일반 BPS 프로그램에는 big endian .z64 원본을 사용하세요.
'''
    write(dist / 'ROM-HASHES.txt', rom_hashes)
    guide = f'''악마성 드라큘라 묵시록 외전 / Legend of Cornell · 한국어 {TAG}

1. Windows x64에서 {EXE}를 실행합니다. 별도 Python 설치는 필요 없습니다.
2. 일본판 원본 롬과 새 출력 파일 경로를 선택합니다.
3. '한글 패치 적용'을 누릅니다. 원본·내장 패치·결과 해시를 확인한 뒤 저장합니다.
4. 생성된 .z64를 새로 부팅하고 게임 안의 저장 데이터를 불러옵니다.

원본은 보존하며 기존 출력 파일은 덮어쓰지 않습니다. 새 이름을 선택하세요.
입력 롬은 16 MiB, 결과는 32 MiB입니다. 세 가지 바이트 순서를 자동 판별합니다.
일반 BPS 프로그램에는 big endian .z64 원본을 사용하세요.
원본 정규화 SHA1: {SOURCE_SHA1}
원본 정규화 SHA256: {SOURCE_SHA256}
한국어 결과 SHA256: {TARGET_SHA256}
EXE SHA256: {sha(dist / EXE)}
BPS SHA256: {manifest['patch_sha256']}

일본어 텍스트 1,665구간과 일본어 타이틀 로고를 한국어로 바꿨습니다.
영어 메뉴·영문 부제·영어 음성은 보존합니다. 띄어쓰기는 8픽셀 반각 공백입니다.
원문 1,410개(중복 포함 1,665구간)를 대조하고 126구간을 바로잡았습니다.
공개판 V0.6은 검수를 마친 로컬 v1.1과 동일한 번역/ROM 내용을 사용합니다.

다른 빌드의 에뮬레이터 빠른 저장 상태를 사용하지 마세요.
새 부팅 후 게임 내부 저장/불러오기를 사용하세요.
저장 형식을 자동 인식하지 못하면 원본과 같은 EEPROM 16K(16 Kbit / 2 KiB)를 지정하세요.

최종 ROM에서 31개 번역 지역, 네 캐릭터, 실제 저장과 새 부팅 불러오기,
아이템 메뉴 및 네 문구의 실제 텍스트 엔진 출력을 확인했습니다.
지역/캐릭터 요청과 대사 출력 시험은 QA용 에뮬레이터 RAM을 사용했습니다.
모든 분기를 처음부터 끝까지 조작해 완주한 검증은 아닙니다.
상세 검수/검증 기록과 스크린샷 설명은 GitHub README를 확인하세요.

저장소: {WEB}
릴리스: {WEB}/releases/tag/{TAG}
원본 ROM과 완성 ROM은 배포 파일에 포함하지 않습니다. 게임의 권리는 원 권리자에게 있습니다.
'''
    write(dist / '사용설명.txt', guide)
    write(ROOT / 'docs/ROM-HASHES.txt', rom_hashes)
    editor_guide = '''묵시록 외전 한국어 텍스트 도구 · V0.6

Cornell_Korean_Editor.exe를 실행합니다. 별도 Python 설치는 필요 없습니다.
첫 실행에서 지원하는 일본판 원본 롬을 선택하면 개인 작업 사본을 준비합니다.
원문/번역/ID 검색, 실제 원문 글꼴과 한글 미리보기, Ctrl+S 저장,
영어 보존·가로 폭·페이지 높이·원본 할당량 검증과 ROM 빌드를 지원합니다.
수정은 translation/user_edits.json, 결과는 work/korean-candidate.z64에 저장됩니다.
검색용 일본어 전사에 오독이 있을 수 있으므로 원문 이미지도 확인하세요.
한글 731자의 픽셀은 고정했습니다. 새 한글 추가 시 Windows 굴림 글꼴을 사용합니다.
소스 실행에는 Python 3.11 이상과 Pillow가 필요합니다.
원본/완성 ROM과 추출된 게임 자산은 이 ZIP에 포함하지 않았습니다.
'''
    write(ROOT / 'text-tool/사용설명.txt', editor_guide)
    # Explicit source directories: never glob the prepared editor's private work/ folder.
    files = []
    for folder, pattern in [('tools', '*.py'), ('translation', '*.json'), ('assets/font', '*'),
                            ('assets/logo', '*'), ('data', '*.json')]:
        for path in sorted((ROOT / 'text-tool' / folder).glob(pattern)):
            if path.is_file():
                files.append(('묵시록외전_텍스트도구/' + path.relative_to(ROOT / 'text-tool').as_posix(), path.read_bytes()))
    files += [('묵시록외전_텍스트도구/' + name, (ROOT / 'text-tool' / name).read_bytes())
              for name in ['analysis/selected-blocks.json', 'requirements.txt', '텍스트_도구_실행.cmd', '사용설명.txt']]
    files.append(('묵시록외전_텍스트도구/Cornell_Korean_Editor.exe', args.editor_exe.read_bytes()))
    archive(dist / EDITOR, files)
    captions = '''스크린샷 설명 · V0.6

01-title: 실제 한글 타이틀. 기존 영어 부제와 메뉴 보존.
02-save-menu / 03-save-complete: 게임 내부 화이트 주얼 저장창과 실제 저장 완료.
04-fresh-load: 새 부팅 후 게임 내부 저장 데이터 불러오기.
05-inventory: 캐리 아이템 메뉴와 한글 지역명.
06~09: 말루스/오르테가/헨리 안내/드라큘라 문구를 실제 MFDS 텍스트 엔진으로 출력한 검수 화면.
이 네 화면은 QA용 RAM으로 문구를 요청한 렌더러 시험이며, 자연스러운 컷신 진행 장면은 아닙니다.
스크린샷 원본은 에뮬레이터가 출력한 640×240이며 README에서는 4:3으로 표시합니다.
'''
    write(ROOT / 'docs/screenshots/README.txt', captions)
    archive(dist / SCREENS, [(p.name, p.read_bytes()) for p in sorted((ROOT / 'docs/screenshots').iterdir()) if p.is_file()])
    archive(dist / WINDOWS, [(EXE, (dist / EXE).read_bytes()), (PATCH, (dist / PATCH).read_bytes()),
                             ('사용설명.txt', guide.encode('utf-8-sig')), ('ROM-HASHES.txt', rom_hashes.encode('utf-8-sig')),
                             ('validation.json', (ROOT / 'docs/validation.json').read_bytes()),
                             ('title.png', (ROOT / 'data/title.png').read_bytes())])
    shutil.copy2(ROOT / 'docs/validation.json', dist / 'validation.json')
    names = [EXE, WINDOWS, PATCH, EDITOR, SCREENS, 'ROM-HASHES.txt', 'validation.json', '사용설명.txt']
    write(dist / 'SHA256SUMS.txt', ''.join(f'{sha(dist / name)}  {name}\n' for name in names))
    jsonwrite(ROOT / 'docs/release-files.json', {name: dict(bytes=(dist/name).stat().st_size, sha256=sha(dist/name)) for name in names})
    readme = f'''<p align="center"><img src="docs/screenshots/01-title.png" width="640" height="480" alt="악마성 드라큘라 묵시록 외전 한국어 타이틀 화면"></p>

**악마성 드라큘라 묵시록 외전 · LEGEND OF CORNELL · N64 일본판 한국어 패치 {TAG}**

일본어 대사·책·아이템 설명·시스템 문구·엔딩 등 **1,665개 텍스트 구간**과 일본어 타이틀 로고를 한국어로 바꿨습니다. 이전 악마성 묵시록 한국어판과 같은 기준으로 **영어 메뉴·영문 부제·영어 음성을 보존**했습니다. 컷신은 게임의 기존 자막 표시·대기 명령을 사용하며, 띄어쓰기는 반각 공백(8픽셀)입니다.

원문 1,410개(중복 포함 1,665구간)를 대조해 **126구간**을 수정했습니다. 자기소개·호칭, 감정 표현과 문장 부호, 제어탑 열쇠 명칭, 분할 대사와 고정 영문을 잇는 문법, 대기 명령 전후의 줄바꿈·공백을 검수했습니다. 공개판 **V0.6**은 검수를 마친 로컬 v1.1과 동일한 번역과 ROM 내용을 사용합니다.

Windows x64에서는 [단일 EXE 패처]({BASE}{EXE}) 또는 [Windows ZIP]({BASE}{WINDOWS})을 받으세요. **Python 설치 없이 실행**합니다. [BPS 단독 패치]({BASE}{PATCH}), [텍스트 편집 도구]({BASE}{EDITOR}), [스크린샷 모음]({BASE}{SCREENS}), [SHA256 목록]({BASE}SHA256SUMS.txt), [ROM 해시 목록]({BASE}ROM-HASHES.txt)도 제공합니다.

1. 패처 EXE를 실행하고 **일본판 원본 롬**을 선택합니다.
2. 새 출력 파일 경로를 고르고 **한글 패치 적용**을 누릅니다.
3. 완료 후 표시된 SHA256을 확인합니다.
4. 생성된 `.z64`를 새로 부팅하고 게임 안의 저장 데이터를 불러옵니다.

원본은 **16 MiB**, 결과는 **32 MiB**입니다. 확장자와 관계없이 `.z64/.v64/.n64`의 실제 바이트 순서를 자동 판별합니다. 원본과 기존 출력 파일은 덮어쓰지 않습니다. 일반 BPS 프로그램에는 big endian `.z64` 원본을 사용하세요.

다른 빌드에서 만든 빠른 저장 상태는 사용하지 마세요. 게임 내부 저장/불러오기를 사용하세요. 저장 방식을 자동 인식하지 못하면 **EEPROM 16K (16 Kbit / 2 KiB)**로 지정합니다.

원본 게임: **Akumajou Dracula Mokushiroku Gaiden - Legend of Cornell (Japan)** / 해외판 제목: **Castlevania: Legacy of Darkness**. 지원 원본 정규화 **SHA1**: `{SOURCE_SHA1}`

| 대상 | SHA256 |
| --- | --- |
| 원본 .z64 (big endian 정규화) | `{SOURCE_SHA256}` |
| 제공된 원본 (v64 순서, 파일 확장자는 .n64) | `{RAW_HASH}` |
| 한국어 결과 .z64 | `{TARGET_SHA256}` |
| Windows EXE | `{sha(dist / EXE)}` |
| BPS 패치 | `{manifest['patch_sha256']}` |
| Windows ZIP | `{sha(dist / WINDOWS)}` |

EXE의 실제 실행으로 세 바이트 순서의 결과 해시 일치를 확인했습니다. 잘못된 원본·손상된 패치·원본 및 기존 출력 덮어쓰기 차단, GUI 시작, 공개 텍스트 도구의 동일 결과 재빌드도 확인했습니다.

473개 자산과 47개 지역 데이터의 압축·크기, 103개 텍스트 풀, 제어 명령·영어 보존, 전체 대사 줄 폭·페이지 높이·N64 체크섬을 검사했습니다. 영문 글꼴·타이틀 영어 부분·다른 타이틀 그래픽·음성 데이터의 원본 일치를 확인했습니다. 최종 ROM에서 **31개 번역 지역, 네 캐릭터, 실제 저장·새 부팅 불러오기, 아이템 메뉴, 네 문구의 MFDS 출력** 등 41개 실행 검사를 통과했습니다.

지역·캐릭터·문구 시험은 QA용 에뮬레이터 RAM 요청을 사용했습니다. **모든 캐릭터의 모든 분기를 처음부터 끝까지 조작해 완주한 검증은 아닙니다.** 검수용 이동·문구 출력 기능은 배포 ROM에 포함하지 않았습니다.

<p><img src="docs/screenshots/02-save-menu.png" width="640" height="480" alt="한글 화이트 주얼 저장창"></p>

화이트 주얼의 한글 저장창

<p><img src="docs/screenshots/03-save-complete.png" width="640" height="480" alt="실제 저장 완료"></p>

게임 내부 저장 완료

<p><img src="docs/screenshots/04-fresh-load.png" width="640" height="480" alt="새 부팅 후 저장 데이터 불러오기"></p>

새 부팅 후 저장 데이터 불러오기

<p><img src="docs/screenshots/05-inventory.png" width="640" height="480" alt="캐리 아이템 메뉴"></p>

캐리의 아이템 메뉴와 한글 지역명

아래 네 화면은 **실제 MFDS 텍스트 엔진에 검수 문구를 요청한 출력 시험**입니다. 자연스러운 컷신 진행을 촬영한 장면은 아닙니다.

<p><img src="docs/screenshots/06-malus-text-preview.png" width="640" height="480" alt="말루스 자기소개 문구 출력 검수"></p>

말루스 자기소개 문구 검수

<p><img src="docs/screenshots/07-ortega-text-preview.png" width="640" height="480" alt="오르테가 대사 출력 검수"></p>

오르테가 대사 검수

<p><img src="docs/screenshots/08-henry-text-preview.png" width="640" height="480" alt="헨리 안내 문구 출력 검수"></p>

헨리 안내 문구 검수

<p><img src="docs/screenshots/09-dracula-text-preview.png" width="640" height="480" alt="드라큘라 대사 출력 검수"></p>

드라큘라 대사 검수. 캡처 원본은 640×240이며 이 페이지에서는 4:3으로 표시합니다.

텍스트 편집 도구는 ZIP을 풀고 `Cornell_Korean_Editor.exe`로 실행합니다. 첫 실행에 지원 원본을 선택하세요. 원문·번역·ID 검색, 원본 글자와 한글 미리보기, Ctrl+S 저장, 폭·페이지·영어 보존 검증과 ROM 빌드를 지원합니다. 검색용 일본어 전사에는 오독이 있을 수 있어 원문 이미지도 함께 확인해야 합니다. 소스로 실행하려면 Python 3.11 이상과 Pillow를 준비하고 `text-tool/텍스트_도구_실행.cmd`를 실행하세요.

패처 소스 실행: `python patcher_app.py`<br>
EXE 빌드: `python -m pip install -r requirements-build.txt` 후 `scripts/build_exe.ps1` 실행<br>
패처 테스트: `CORNELL_TEST_ROM` 환경 변수에 지원 원본 경로를 지정하고 `python -m unittest discover -s tests -v` 실행<br>
완성 EXE 검사: `python scripts/verify_exe.py "원본 롬 경로"`

[검수 기록](docs/proofreading.json), [검증 기록](docs/validation.json), [배포 파일 해시](docs/release-files.json), [스크린샷 설명](docs/screenshots/README.txt)을 제공합니다. 원본 ROM·완성 ROM·세이브·에뮬레이터 상태는 저장소와 배포 파일에 포함하지 않았습니다. 게임의 권리는 원 권리자에게 있습니다.

구조 참고: [fliperama86/cvlod_recomp](https://github.com/fliperama86/cvlod_recomp), [k64ret/cv64](https://github.com/k64ret/cv64). 로고 제작 정보는 [generation.txt](text-tool/assets/logo/generation.txt)에 있습니다.
'''
    write(ROOT / 'README.md', readme)
    release = f'''악마성 드라큘라 묵시록 외전 / LEGEND OF CORNELL 일본판 한국어 패치 **{TAG}**입니다.

![한글 타이틀](https://raw.githubusercontent.com/{REPO}/{TAG}/docs/screenshots/01-title.png)

- Windows 단일 EXE: `{EXE}` — Python 설치 없이 실행
- Windows 묶음: `{WINDOWS}` — EXE, BPS, 사용법, ROM 해시, 검증 기록
- BPS: `{PATCH}` — big endian .z64 원본에 적용
- 텍스트 편집기: `{EDITOR}` — 최초 실행 시 본인의 일본판 원본 필요
- 스크린샷: `{SCREENS}` / 파일 해시: `SHA256SUMS.txt`

일본어 1,665구간과 타이틀 로고를 한국어로 바꾸고, 전체 원문 대조로 126구간을 수정했습니다. 영어 메뉴·영문 부제·음성을 유지합니다. 공개판 V0.6은 검수를 마친 로컬 v1.1과 같은 내용입니다.

원본 16 MiB → 결과 32 MiB. EXE는 세 바이트 순서를 자동 인식하고 원본과 기존 출력을 덮어쓰지 않습니다. 새 ROM을 부팅하고 게임 내부 저장 데이터를 불러오세요. EEPROM 자동 인식 실패 시 16K(16 Kbit / 2 KiB)를 지정하세요.

원본 정규화 SHA1: `{SOURCE_SHA1}`<br>
원본 정규화 SHA256: `{SOURCE_SHA256}`<br>
제공된 원본(v64 순서) SHA256: `{RAW_HASH}`<br>
한국어 결과 SHA256: `{TARGET_SHA256}`

EXE 실제 실행·세 순서 패치 결과, GUI, 오류 차단, 편집기 동일 결과 빌드를 확인했습니다. 31개 번역 지역·네 캐릭터·실제 저장/새 부팅 불러오기·메뉴·대사 출력 등 41개 실행 검사를 통과했습니다. 전체 분기 완주 검증은 아니며, 대사 검수 스크린샷은 QA용 RAM으로 텍스트 엔진을 호출한 화면입니다.

여러 스크린샷과 상세 내용은 [저장소 README]({WEB}#readme), 검수/검증 기록은 `docs/`에 있습니다. 원본 ROM과 완성 ROM은 포함하지 않습니다.
'''
    write(ROOT / 'RELEASE-NOTES.md', release)
    print(json.dumps(dict(files=names + ['SHA256SUMS.txt'], exe_sha256=sha(dist / EXE)), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
