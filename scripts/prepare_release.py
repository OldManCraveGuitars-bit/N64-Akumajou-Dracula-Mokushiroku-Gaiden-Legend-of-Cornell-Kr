"""Assemble the reviewed release with current verification and an explicit allowlist."""
import argparse,hashlib,json,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from patcher_core import VERSION,SOURCE_SHA1,SOURCE_SHA256,TARGET_SHA256
TAG='V'+VERSION
WEB='https://github.com/OldManCraveGuitars-bit/N64-Akumajou-Dracula-Mokushiroku-Gaiden-Legend-of-Cornell-Kr'
BASE=WEB+'/releases/download/'+TAG+'/'
EXE=f'N64-Legend-of-Cornell-Kr-{TAG}-Patcher.exe'
PATCH=f'Legend-of-Cornell-Korean-{TAG}.bps'
WINDOWS=f'N64-Legend-of-Cornell-Kr-{TAG}-Windows.zip'
EDITOR=f'Text-Tool-{TAG}.zip';SCREENS=f'Screenshots-{TAG}.zip'
RAW_HASH='c90e4e11e90a8688d655f59a3ad069814cfa24c2b55e5a959588b03dc4585a65'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,text):path.write_text(text,encoding='utf-8')
def jsonwrite(path,value):write(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def archive(path,files):
    with zipfile.ZipFile(path,'w') as z:
        for name,data in files:
            info=zipfile.ZipInfo(name,(2026,11,15,0,0,0))
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all('/work/' not in n and '/.qa/' not in n and not n.lower().endswith(('.z64','.n64','.v64','.sav','.srm','.eep','.state','.dll')) for n in z.namelist())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--editor-exe',type=Path,required=True);args=ap.parse_args()
    dist=ROOT/'dist';manifest=read(ROOT/'data/manifest.json');frozen=read(dist/'patcher-verification.json')
    assert frozen['all_passed'] and frozen['target_sha256']==TARGET_SHA256 and frozen['executable_sha256']==sha(dist/EXE)
    assert sha(ROOT/'data'/PATCH)==manifest['patch_sha256']
    assert sha(ROOT/'text-tool/work/korean-candidate.z64')==TARGET_SHA256
    verification=read(ROOT/'docs/translation-validation.json');assert verification['target_sha256']==TARGET_SHA256
    verification['patcher']=frozen;verification['public_editor_source_rebuilt_same_target']=True
    portable=read(dist/'editor-verification.json') if (dist/'editor-verification.json').exists() else {}
    if portable.get('success') and portable.get('target_sha256')==TARGET_SHA256:verification['public_portable_editor']=portable
    jsonwrite(ROOT/'docs/validation.json',verification)
    shutil.copy2(ROOT/'data'/PATCH,dist/PATCH)
    hashes=f'''악마성 드라큘라 묵시록 외전 / Legend of Cornell · {TAG}
원본: Akumajou Dracula Mokushiroku Gaiden - Legend of Cornell (Japan)
원본: 16,777,216 bytes (16 MiB) / 결과: 33,554,432 bytes (32 MiB)

원본 SHA1 (big endian .z64 정규화): {SOURCE_SHA1}
원본 SHA256 (big endian .z64 정규화): {SOURCE_SHA256}
제공된 원본 SHA256 (v64 순서 / 파일 확장자는 .n64): {RAW_HASH}
한국어 결과 SHA256 (.z64): {TARGET_SHA256}

EXE는 확장자 대신 파일 헤더로 바이트 순서를 판별하고 원본을 검증합니다.
일반 BPS 프로그램에는 big endian .z64 원본을 사용하세요.
'''
    write(dist/'ROM-HASHES.txt',hashes);write(ROOT/'docs/ROM-HASHES.txt',hashes)
    guide=f'''악마성 드라큘라 묵시록 외전 / Legend of Cornell · 한국어 {TAG}

Windows x64에서 {EXE}를 실행합니다. Python 설치는 필요 없습니다.
일본판 원본 롬과 새 출력 경로를 선택한 뒤 '한글 패치 적용'을 누르세요.
원본·패치·결과 해시를 확인한 뒤 별도 .z64 파일을 만듭니다.
.z64/.v64/.n64의 실제 바이트 순서를 자동 판별합니다.
입력은 16 MiB, 출력은 32 MiB입니다. 원본과 기존 출력 파일은 덮어쓰지 않습니다.
일반 BPS 프로그램에는 big endian .z64 원본을 사용하세요.

V0.6.1 수정
- '저장 중입니다'가 '장 중입니다'로 보이던 시작 주소 오류를 수정했습니다.
- 예언 문구와 헨리 안내 제목의 같은 주소 오류도 수정했습니다.
- 상점 보유 안내를 '보유 수량: 0개'로 바꾸고 설명문을 실제 창 폭 안에 배치했습니다.
- 1,665구간 전체를 재대조해 오역·조사·띄어쓰기·표기 등 65구간을 수정했습니다.
- 원본 碧眼을 확인해 '붉은 눈'을 '푸른 눈'으로 바로잡았습니다.
- 공백은 U+0020 반각 8픽셀, 한글은 16픽셀입니다.

새 ROM을 부팅하고 게임 안의 저장 데이터를 불러오세요.
다른 빌드에서 만든 에뮬레이터 빠른 저장 상태는 사용하지 마세요.
저장 방식을 자동 인식하지 못하면 EEPROM 16K(16 Kbit / 2 KiB)를 지정하세요.
영어 메뉴·영문 부제·음성은 원본과 같습니다.

원본 정규화 SHA1: {SOURCE_SHA1}
원본 정규화 SHA256: {SOURCE_SHA256}
한국어 결과 SHA256: {TARGET_SHA256}
EXE SHA256: {sha(dist/EXE)}
BPS SHA256: {manifest['patch_sha256']}

최종 ROM에서 31개 번역 지역, 네 캐릭터, 상점 구매·수량·설명,
저장 중 문구, 실제 저장과 새 부팅 불러오기, 옵션, 대사 출력 등 44개 실행 검사를 통과했습니다.
지역·메뉴·문구 요청 시험에는 QA용 에뮬레이터 RAM을 사용했습니다.
모든 분기를 처음부터 끝까지 직접 조작해 완주한 검증은 아닙니다.
저장소: {WEB}
릴리스: {WEB}/releases/tag/{TAG}
원본/완성 ROM은 배포 파일에 포함하지 않습니다. 게임의 권리는 원 권리자에게 있습니다.
'''
    write(dist/'USAGE-KO.txt',guide)
    editor_guide=f'''묵시록 외전 한국어 텍스트 도구 · {TAG}
Cornell_Korean_Editor.exe를 실행하고 첫 실행에서 일본판 원본을 선택하세요.
별도 Python 설치는 필요 없습니다. 소스 실행에는 Python 3.11 이상과 Pillow가 필요합니다.
원문/번역/ID 검색, 실제 원문 글꼴·한글 미리보기, Ctrl+S 저장과 ROM 빌드를 지원합니다.
수정: translation/user_edits.json / 결과: work/korean-candidate.z64
일반 대사 240px, 상점·아이템 설명 208px, 상점 보유 안내 128px 제한을 검사합니다.
영어·제어 명령·원본 할당 공간·페이지 높이도 검사합니다.
반각 공백 U+0020은 8px입니다. 현재 한글 731자의 글꼴 픽셀은 고정했습니다.
새 한글을 추가할 때는 Windows 굴림 글꼴을 사용합니다.
검색용 일본어 한자 전사에는 오독이 있을 수 있으므로 원문 이미지도 확인하세요.
원본/완성 ROM과 추출된 게임 자산은 ZIP에 포함하지 않았습니다.
'''
    write(ROOT/'text-tool/사용설명.txt',editor_guide)
    files=[]
    for folder,pattern in [('tools','*.py'),('translation','*.json'),('assets/font','*'),('assets/logo','*'),('data','*.json')]:
        for p in sorted((ROOT/'text-tool'/folder).glob(pattern)):
            if p.is_file():files.append(('묵시록외전_텍스트도구/'+p.relative_to(ROOT/'text-tool').as_posix(),p.read_bytes()))
    files += [('묵시록외전_텍스트도구/'+name,(ROOT/'text-tool'/name).read_bytes()) for name in ['analysis/selected-blocks.json','requirements.txt','텍스트_도구_실행.cmd','사용설명.txt']]
    files.append(('묵시록외전_텍스트도구/Cornell_Korean_Editor.exe',args.editor_exe.read_bytes()))
    archive(dist/EDITOR,files)
    if portable.get('editor_archive_sha256') and portable.get('target_sha256')==TARGET_SHA256:assert portable['editor_archive_sha256']==sha(dist/EDITOR)
    screenshots=read(ROOT/'docs/screenshots/index.json')
    screenfiles=[(s['file'],(ROOT/'docs/screenshots'/s['file']).read_bytes()) for s in screenshots]
    screenfiles += [(n,(ROOT/'docs/screenshots'/n).read_bytes()) for n in ['README.txt','index.json']]
    archive(dist/SCREENS,screenfiles)
    archive(dist/WINDOWS,[(EXE,(dist/EXE).read_bytes()),(PATCH,(dist/PATCH).read_bytes()),('사용설명.txt',guide.encode('utf-8-sig')),
                         ('ROM-HASHES.txt',hashes.encode('utf-8-sig')),('validation.json',(ROOT/'docs/validation.json').read_bytes()),
                         ('검수내역.txt',(ROOT/'docs/proofreading-2026-11-15.txt').read_bytes())])
    shutil.copy2(ROOT/'docs/validation.json',dist/'validation.json')
    names=[EXE,WINDOWS,PATCH,EDITOR,SCREENS,'ROM-HASHES.txt','validation.json','USAGE-KO.txt']
    write(dist/'SHA256SUMS.txt',''.join(f'{sha(dist/n)}  {n}\n' for n in names))
    jsonwrite(ROOT/'docs/release-files.json',{n:dict(bytes=(dist/n).stat().st_size,sha256=sha(dist/n)) for n in names})
    body=f'''<p align="center"><img src="docs/screenshots/01-title.png" width="640" height="480" alt="한글 타이틀 화면"></p>

**악마성 드라큘라 묵시록 외전 · LEGEND OF CORNELL · N64 일본판 한국어 패치 {TAG}**

일본어 텍스트 **1,665구간**과 일본어 타이틀 로고를 한국어로 바꿨습니다. 영어 메뉴·영문 부제·영어 음성은 보존합니다. 띄어쓰기는 **반각 공백 U+0020, 8픽셀**이며 한글 글자는 16픽셀입니다.

**V0.6.1은 전체 재검수와 UI 잘림 수정판입니다.** 전체 1,665구간(고유 원문 1,410개, 원문·번역 쌍 1,420개)을 다시 대조하고 65구간을 수정했습니다.

- 저장 진행 문구가 **'장 중입니다'**로 보이던 시작 주소 오류를 수정했습니다. 예언 문구와 헨리 안내 제목의 같은 오류도 고쳤습니다.
- 상점 하단 안내를 **'보유 수량: 0개'**로 바꿔 소지금 칸과 겹치지 않게 했습니다. 구매 후 보유 개수도 확인했습니다.
- 상점·아이템 설명을 실제 208px 폭 안에 재배치했습니다. 보유 안내는 128px, 일반 대사는 240px 제한을 검사합니다.
- 원본 글자를 직접 확인해 **'붉은 눈' → '푸른 눈'** 등 오역을 바로잡고, 조사·버튼 이름·숫자·대기 명령 전후의 공백을 다듬었습니다.

[**Windows EXE 패처 다운로드**]({BASE}{EXE}) · [Windows ZIP]({BASE}{WINDOWS}) · [BPS]({BASE}{PATCH}) · [텍스트 편집기]({BASE}{EDITOR}) · [스크린샷]({BASE}{SCREENS}) · [SHA256 목록]({BASE}SHA256SUMS.txt)

1. EXE를 실행하고 일본판 원본 롬을 선택합니다. Python 설치는 필요 없습니다.
2. 새 출력 경로를 정한 뒤 **한글 패치 적용**을 누릅니다.
3. 결과 해시를 확인하고 새 `.z64`를 부팅합니다.
4. 게임 안의 저장 데이터를 불러옵니다. 다른 빌드의 빠른 저장 상태는 사용하지 마세요.

원본은 **16 MiB**, 결과는 **32 MiB**입니다. EXE는 `.z64/.v64/.n64`의 바이트 순서를 자동 인식하고 원본과 기존 출력 파일을 보존합니다. 일반 BPS 프로그램은 big endian `.z64` 원본에 적용하세요. 저장 방식 자동 인식 실패 시 **EEPROM 16K (16 Kbit / 2 KiB)**를 지정합니다.

지원 원본: **Akumajou Dracula Mokushiroku Gaiden - Legend of Cornell (Japan)** / 해외판 제목: Castlevania: Legacy of Darkness. 원본 정규화 **SHA1**: `{SOURCE_SHA1}`

| 대상 | SHA256 |
| --- | --- |
| 원본 .z64 (big endian 정규화) | `{SOURCE_SHA256}` |
| 제공된 원본 (v64 순서, 확장자는 .n64) | `{RAW_HASH}` |
| 한국어 결과 .z64 | `{TARGET_SHA256}` |
| Windows EXE | `{sha(dist/EXE)}` |
| BPS | `{manifest['patch_sha256']}` |
| Windows ZIP | `{sha(dist/WINDOWS)}` |

473개 자산·47개 지역 데이터·103개 텍스트 풀, N64 체크섬, 영어·음성 보존, 전체 줄 폭과 페이지 높이를 검사했습니다. 최종 ROM에서 **31개 번역 지역·네 캐릭터·상점·저장/새 부팅 불러오기·메뉴·텍스트 출력 등 44개 실행 검사**를 통과했습니다. EXE의 세 바이트 순서 적용, 오류 차단, GUI, 편집기의 동일 결과 재빌드도 검사했습니다.

지역·메뉴 요청과 대사 출력에는 QA용 에뮬레이터 RAM을 사용했습니다. **모든 캐릭터의 모든 분기를 처음부터 끝까지 조작해 완주한 검증은 아닙니다.** 배포 ROM에는 QA용 이동·문구 출력 기능이 들어 있지 않습니다.

<p><img src="docs/screenshots/02-saving.png" width="640" height="480" alt="저장 중입니다 정상 표시"></p>

짧게 지나가는 저장 안내를 매 프레임 기록해 첫 글자까지 정상 표시되는 것을 확인했습니다. [V0.6에서 재현한 수정 전 화면](docs/screenshots/12-before-saving.png)과 비교할 수 있습니다.

<p><img src="docs/screenshots/06-shop-zero.png" width="640" height="480" alt="상점 보유 수량 0개"></p>

보유 안내와 소지금 칸이 겹치지 않습니다.

<p><img src="docs/screenshots/07-shop-description.png" width="640" height="480" alt="상점 아이템 설명 3행"></p>

아이템 효과를 유지하면서 설명을 창 안에 배치했습니다.

<p><img src="docs/screenshots/08-shop-owned.png" width="640" height="480" alt="상점 구매 후 보유 수량"></p>

실제 구매 후 개수·잔액 표시

<p><img src="docs/screenshots/03-save-complete.png" width="640" height="480" alt="게임 내부 저장 완료"></p>

게임 내부 저장 완료. [새 부팅 후 불러오기](docs/screenshots/04-fresh-load.png), [일시정지 메뉴](docs/screenshots/05-inventory.png)도 확인했습니다.

<p><img src="docs/screenshots/09-prophecy-blue-eyes.png" width="640" height="480" alt="푸른 눈 오역 수정"></p>

원본의 碧眼(푸른 눈)을 확인해 수정했습니다. 이 화면과 [헨리 안내 제목](docs/screenshots/10-henry-title.png), [예언 도입 문구](docs/screenshots/11-prophecy-title.png)는 실제 MFDS 텍스트 엔진에 QA 문구를 요청한 출력 시험이며, 자연스러운 컷신 진행 장면은 아닙니다.

텍스트 도구는 ZIP을 풀어 `Cornell_Korean_Editor.exe`를 실행하고 첫 실행에 지원 원본을 선택합니다. 원문·번역·ID 검색, 실제 글꼴 미리보기, Ctrl+S 저장, 영어·표시 폭·할당량 검증과 ROM 빌드를 지원합니다. 소스 실행은 Python 3.11 이상과 Pillow가 필요합니다. 검색용 일본어 전사에는 오독이 있을 수 있으므로 원문 이미지도 확인하세요.

패처 소스: `python patcher_app.py`<br>
EXE 빌드: `python -m pip install -r requirements-build.txt` 후 `scripts/build_exe.ps1`<br>
테스트: `CORNELL_TEST_ROM` 환경 변수에 지원 원본을 지정하고 `python -m unittest discover -s tests -v`<br>
완성 EXE 검사: `python scripts/verify_exe.py "원본 롬 경로"`

[이번 검수 기록 JSON](docs/proofreading-2026-11-15.json) · [변경 전후와 사유](docs/proofreading-2026-11-15.txt) · [주소 검사](docs/text-entry-audit.json) · [최종 검증](docs/validation.json) · [배포 파일 해시](docs/release-files.json) · [스크린샷 설명](docs/screenshots/README.txt)

[이전 V0.6 릴리스]({WEB}/releases/tag/V0.6)는 보존했습니다. 원본 ROM·완성 ROM·세이브·에뮬레이터 상태는 저장소와 배포 파일에 포함하지 않았습니다. 게임의 권리는 원 권리자에게 있습니다.

구조 참고: [fliperama86/cvlod_recomp](https://github.com/fliperama86/cvlod_recomp), [k64ret/cv64](https://github.com/k64ret/cv64).
'''
    write(ROOT/'README.md',body)
    release=f'''악마성 드라큘라 묵시록 외전 / LEGEND OF CORNELL 일본판 한국어 패치 **{TAG}**입니다.

![타이틀](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Akumajou-Dracula-Mokushiroku-Gaiden-Legend-of-Cornell-Kr/{TAG}/docs/screenshots/01-title.png)

- '장 중입니다' → **'저장 중입니다.'**: 앞 글자를 건너뛰던 주소 오류와 같은 유형의 두 문구를 수정했습니다.
- 상점 보유 안내 **'보유 수량: 0개'**, 소지금 칸, 아이템 설명의 잘림을 고쳤습니다.
- 1,665구간 전체를 다시 대조하고 오역·조사·띄어쓰기 등 **65구간**을 수정했습니다.
- 공백은 **U+0020 반각 8px**입니다. 영어 메뉴·영문 부제·음성은 유지합니다.

Windows x64: `{EXE}` 또는 `{WINDOWS}`. Python 설치 없이 실행합니다. 일본판 원본에 적용하고 새 ROM을 부팅한 뒤 게임 내부 저장을 불러오세요. 원본/기존 출력은 덮어쓰지 않습니다. 원본 16 MiB → 결과 32 MiB, 세 바이트 순서를 자동 인식합니다.

`{PATCH}`는 big endian .z64 원본용입니다. `{EDITOR}`는 첫 실행에 본인의 원본이 필요합니다. 스크린샷·변경 내역·검증·SHA256 목록도 제공합니다.

원본 정규화 SHA1: `{SOURCE_SHA1}`<br>
원본 정규화 SHA256: `{SOURCE_SHA256}`<br>
제공된 원본(v64 순서) SHA256: `{RAW_HASH}`<br>
한국어 결과 SHA256: `{TARGET_SHA256}`

31개 지역·네 캐릭터·상점·저장/새 부팅 불러오기·메뉴·텍스트 출력 등 최종 ROM 실행 검사 44건과 EXE/편집기 검사를 통과했습니다. 모든 플레이 분기를 완주한 검증은 아닙니다. 일부 실행 검사는 QA용 RAM 요청을 사용했습니다.

[상세 내용·스크린샷·검수 기록]({WEB}#readme). V0.6은 별도 보존했습니다. 원본/완성 ROM은 배포 파일에 포함하지 않습니다.
'''
    write(ROOT/'RELEASE-NOTES.md',release)
    print(json.dumps(dict(version=TAG,files=names+['SHA256SUMS.txt'],exe_sha256=sha(dist/EXE)),indent=2))

if __name__=='__main__':main()
