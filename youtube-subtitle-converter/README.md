# 자막 변환기 (YouTube → 한글 자막 .txt)

유튜브 주소만 넣으면 **한국어 음성을 텍스트 자막으로** 바꿔 저장하는 웹앱입니다.
듣지 못하는 학생·직장인을 위한 시각 자막 서비스를 목표로 만들었어요.

- 연그레이 배경 + 그리너리 포인트의 심플·미니멀 화면
- 타임스탬프 켜기/끄기, 결과 미리보기, `.txt` 저장, 키워드 검색·자동 스크롤, 글자 크기 조절, 모바일 반응형

---

## 🖱️ 무엇을 눌러야 하나요? (OS별 한눈에)

> **개발자가 아니어도 됩니다.** 파이썬이 없으면 설치 파일이 알아서 설치를 안내/진행하고,
> 끝나면 **브라우저가 자동으로 열려 실행 결과 화면**이 뜹니다.

| 내 컴퓨터 | 눌러야 하는 것 | 방법 |
|---|---|---|
| 🟦 **Windows** | **`install.bat`** | 내려받아 **더블클릭** (PowerShell·WSL 불필요) |
| 🍏 **macOS** | **`install.sh`** | 터미널에 아래 한 줄 붙여넣기 |
| 🟩 **Linux / WSL** | **`install.sh`** | 터미널에 아래 한 줄 붙여넣기 |

---

## 🟦 Windows — 가장 쉬운 길 (더블클릭)

1. 아래 파일을 내려받습니다 (오른쪽 클릭 → **다른 이름으로 링크 저장**):
   <https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.bat>
2. 내려받은 **`install.bat`** 을 **더블클릭**합니다.
3. 만약 파란 경고창 *"Windows의 PC 보호"* 가 뜨면 → **추가 정보** → **실행** 을 누르세요.
   (내가 직접 받은 설치 파일이라 안전합니다.)
4. 검은 창에서 설치가 진행되고, 끝나면 **브라우저가 자동으로 열립니다**
   → 주소창에 `http://127.0.0.1:5123`

> 파이썬이 없으면 `install.bat` 이 자동 설치를 안내합니다.
> 이미 설치돼 있으면 그 단계는 **건너뛰고(pass)** 바로 다음으로 갑니다.

<details>
<summary>명령창을 쓰는 게 편하다면 (선택)</summary>

```bat
REM 대상(실행 위치): 🟦 Windows — cmd(명령 프롬프트). PowerShell 아님
curl -L -o "%USERPROFILE%\Downloads\install.bat" "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.bat" && "%USERPROFILE%\Downloads\install.bat"
```
</details>

---

## 🍏 macOS · 🟩 Linux · WSL — 터미널 한 줄

```bash
# 대상(실행 위치): 🟩 Linux·macOS 터미널 (WSL 포함) — bash
curl -sSL https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.sh | bash
```

파이썬이 없으면 스크립트가 자동 설치를 시도하고, 끝나면 브라우저에서
`http://127.0.0.1:5123` 을 열면 됩니다.

---

## 이미 폴더를 받아둔 경우 (재실행)

설치가 한 번 끝난 뒤에는 매번 내려받을 필요 없이, 폴더 안의 시작 파일만 누르면 됩니다.

| OS | 재실행 파일 |
|---|---|
| 🟦 Windows | **`시작_윈도우.bat`** 더블클릭 |
| 🍏🟩 mac/Linux/WSL | `bash start.sh` |

---

## 명령줄(CLI)로 쓰고 싶다면

```bash
# 대상(실행 위치): 🟩 Linux·macOS 터미널 (WSL 포함) — bash
.venv/bin/python cli.py "<유튜브 주소>" --timestamps --output 자막.txt
```

옵션: `--timestamps`(타임스탬프 포함), `--output`(저장 파일명), `--model`(whisper 모델 크기), `--cookies`(브라우저 쿠키로 봇 차단 우회).

---

## 설치가 끝나면 남는 증거 파일 (`~/youtube-subtitle-converter/.oneshot/`)

- `result.json` — 성공/실패(PASS/FAIL)와 증거 수준(PROVEN 등)
- `manifest.json`, `SHA256SUMS.txt` — 내려받은 파일 목록·무결성
- `install.log`, `server.log` — 진행·서버 로그

문제가 생기면 `install.log` 를 먼저 확인하세요.

---

## 안내

- 완전한 한국어 음성 인식(faster-whisper, 첫 실행 시 모델 자동 다운로드)
- 유튜브 봇 차단이 뜨면 로그인된 브라우저 쿠키로 자동 재시도합니다
- 개인 학습·접근성 목적. 저작권이 있는 영상의 자막화는 각자 책임하에 사용하세요.
