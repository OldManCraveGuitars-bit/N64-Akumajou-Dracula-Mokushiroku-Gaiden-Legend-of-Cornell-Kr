악마성 드라큘라 묵시록 외전 / LEGEND OF CORNELL 일본판 한국어 패치 **V0.6**입니다.

![한글 타이틀](https://raw.githubusercontent.com/OldManCraveGuitars-bit/N64-Akumajou-Dracula-Mokushiroku-Gaiden-Legend-of-Cornell-Kr/V0.6/docs/screenshots/01-title.png)

- Windows 단일 EXE: `N64-Legend-of-Cornell-Kr-V0.6-Patcher.exe` — Python 설치 없이 실행
- Windows 묶음: `N64-Legend-of-Cornell-Kr-V0.6-Windows.zip` — EXE, BPS, 사용법, ROM 해시, 검증 기록
- BPS: `Legend-of-Cornell-Korean-V0.6.bps` — big endian .z64 원본에 적용
- 텍스트 편집기: `Text-Tool-V0.6.zip` — 최초 실행 시 본인의 일본판 원본 필요
- 스크린샷: `Screenshots-V0.6.zip` / 파일 해시: `SHA256SUMS.txt`

일본어 1,665구간과 타이틀 로고를 한국어로 바꾸고, 전체 원문 대조로 126구간을 수정했습니다. 영어 메뉴·영문 부제·음성을 유지합니다. 공개판 V0.6은 검수를 마친 로컬 v1.1과 같은 내용입니다.

원본 16 MiB → 결과 32 MiB. EXE는 세 바이트 순서를 자동 인식하고 원본과 기존 출력을 덮어쓰지 않습니다. 새 ROM을 부팅하고 게임 내부 저장 데이터를 불러오세요. EEPROM 자동 인식 실패 시 16K(16 Kbit / 2 KiB)를 지정하세요.

원본 정규화 SHA1: `50439acb5784bea3a4bbba5188c2aeaa1442099d`<br>
원본 정규화 SHA256: `51a0443883f3f94b20b6fb9a8688631c51bc7feafb143c51e48dc7198adfd1ca`<br>
제공된 원본(v64 순서) SHA256: `c90e4e11e90a8688d655f59a3ad069814cfa24c2b55e5a959588b03dc4585a65`<br>
한국어 결과 SHA256: `55d8eece2108ed6dd3691f36d5e9572b9f60acb9aacc57f626df6ccd6d26b2db`

EXE 실제 실행·세 순서 패치 결과, GUI, 오류 차단, 편집기 동일 결과 빌드를 확인했습니다. 31개 번역 지역·네 캐릭터·실제 저장/새 부팅 불러오기·메뉴·대사 출력 등 41개 실행 검사를 통과했습니다. 전체 분기 완주 검증은 아니며, 대사 검수 스크린샷은 QA용 RAM으로 텍스트 엔진을 호출한 화면입니다.

여러 스크린샷과 상세 내용은 [저장소 README](https://github.com/OldManCraveGuitars-bit/N64-Akumajou-Dracula-Mokushiroku-Gaiden-Legend-of-Cornell-Kr#readme), 검수/검증 기록은 `docs/`에 있습니다. 원본 ROM과 완성 ROM은 포함하지 않습니다.
