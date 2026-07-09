# 자막 변환기 (YouTube → 한글 자막 .txt)

유튜브 주소만 넣으면 **한국어 음성을 텍스트 자막으로** 바꿔 저장하는 웹앱입니다.
듣지 못하는 학생·직장인을 위한 시각 자막 서비스를 목표로 만들었어요.

- 연그레이 배경 + 그리너리 포인트의 심플·미니멀 화면
- 타임스탬프 켜기/끄기, 결과 미리보기, `.txt` 저장, 키워드 검색·자동 스크롤, 실시간 진행률, 글자 크기 조절, 모바일 반응형 + PWA

---

## ⚡ 바로 설치 — 내 환경 골라 그대로 복붙

> 맨 앞 `#`(PowerShell) / `REM`(cmd) 줄은 **설명(주석)**이라 같이 붙여넣어도 에러 없이 넘어갑니다.
> 파이썬이 없으면 자동 설치를 안내하고, 끝나면 **브라우저가 자동으로 열립니다.**

**🟦 Windows — PowerShell (파란 창 `PS C:\>`)**
```powershell
# 대상: Windows PowerShell — 아래 한 줄만 진짜 명령. 이 #줄은 설명이라 안전.
irm https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.ps1 | iex
```

**🟦 Windows — 명령 프롬프트 cmd (검은 창 `C:\>`)**
```bat
REM 대상: Windows cmd — 받은 뒤 파일이 있으면에만 실행(검사 후 실행)
curl -fL -o "%TEMP%\ysc-install.bat" "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.bat" && if exist "%TEMP%\ysc-install.bat" call "%TEMP%\ysc-install.bat"
```

**🍏 macOS · 🟩 Linux · WSL — 터미널**
```bash
# 대상: Linux·macOS 터미널(WSL 포함) — bash
curl -sSL https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.sh | bash
```

타이핑이 싫으면 → 아래 **가장 쉬운 길(더블클릭)** 로 가세요. 폰은 → **📱 폰에서 쓰기** 참고.

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
<summary>명령창을 쓰는 게 편하다면 (선택) — 창에 맞는 한 줄</summary>

> 맨 앞 `#`(PowerShell) / `REM`(cmd) 줄은 **설명(주석)** 이라 같이 붙여넣어도 에러가 안 납니다.
> 빨간 글씨가 떠도 컴퓨터는 절대 안 부서지니 안심하세요.

**파란 창(PowerShell, `PS C:\>`) 이면 — 아래 두 줄 통째로 붙여넣기:**

```powershell
# 대상: Windows PowerShell — 아래 한 줄만 진짜 명령이에요. 이 #줄은 설명이라 안전.
irm https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.ps1 | iex
```

**검은 창(명령 프롬프트 cmd, `C:\>`) 이면 — 아래 두 줄 통째로 붙여넣기:**

```bat
REM 대상: Windows cmd — 받은 뒤 "파일이 있으면"에만 실행 (검사 후 실행)
curl -fL -o "%TEMP%\ysc-install.bat" "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.bat" && if exist "%TEMP%\ysc-install.bat" call "%TEMP%\ysc-install.bat"
```

원칙: ① 진입점(`install.bat`/`install.ps1`)은 **순수 영문(ASCII)** — 한국어 윈도우(CP949)에서도 안 깨짐. ② 받은 뒤 **파일 존재를 확인하고 나서** 실행. ③ 한글 안내는 전부 파이썬(`oneshot.py`)이 출력.
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

## 📱 폰(안드로이드 · 아이폰)에서 쓰기

### 🤖 안드로이드 — 앱 설치 (APK, PC 불필요 목표)
폰에 직접 설치하는 **독립 앱**입니다. QR 스캔 한 번 또는 아래 링크로 받으세요:

<img src="android/apk-qr.png" alt="APK 다운로드 QR" width="200">

**https://github.com/rainbowww/skills/releases/download/android-latest/subtitle-converter.apk**

QR 스캔(또는 링크) → 다운로드 → 탭해서 설치 → "이 출처 허용" 한 번.
자세한 건 [`android/README.md`](android/README.md). (현재 1단계: 설치·화면·주소 인식 /
다음 단계에서 폰 온디바이스 음성 인식 추가)

### 🌐 아이폰·그 외 — 브라우저로 (PC 필요)
아래 방식은 폰에 아무것도 설치 안 해도 됩니다. 자막 변환(음성 인식)은 PC가 하고,
폰은 같은 와이파이로 **화면만** 봅니다. 안드로이드·아이폰 브라우저 모두 지원합니다.

**1단계 — PC를 폰 접속 모드로 켜기** (같은 와이파이의 폰이 접속 가능하게):

```bash
# 대상(실행 위치): 🟩 Linux·macOS 터미널 (WSL 포함) — bash
YSC_HOST=0.0.0.0 .venv/bin/python app.py
```

```powershell
# 대상: 🟦 Windows PowerShell — 폰 접속 모드로 실행
$env:YSC_HOST="0.0.0.0"; .\.venv\Scripts\python app.py
```

실행하면 화면에 **폰에서 열 주소**(`http://<이-PC-IP>:5123`)가 찍힙니다.
※ 윈도우 첫 실행 시 방화벽 허용 창이 뜨면 **'허용'**을 누르세요(같은 와이파이 안에서만 열립니다).

**2단계 — 폰에서 열기.** PC 화면에 뜬 **QR 코드를 폰 카메라로 스캔**하면 바로 열립니다
(IP 타이핑 불필요!). 또는 폰 브라우저 주소창에 그 주소를 입력해도 됩니다.
(안드로이드 크롬·삼성인터넷, 아이폰 사파리 모두 지원)

> 📌 **안드로이드는 스토어에서 "내려받는" 앱이 아닙니다.** 위처럼 폰 브라우저로 열고
> → 메뉴 ‘앱 설치 / 홈 화면에 추가’ 하면 아이콘이 생겨 앱처럼 쓰는 방식(PWA)이에요.

**3단계(선택) — 앱처럼 홈 화면에 설치 (PWA):**
- 안드로이드 크롬/삼성인터넷: 메뉴 → **‘앱 설치’ / ‘홈 화면에 추가’**
- 아이폰 사파리: 공유 → **‘홈 화면에 추가’**
- 설치하면 아이콘이 생기고, 전체화면 앱처럼 실행됩니다.
  (껍데기는 오프라인에서도 뜨지만, 실제 변환은 PC가 켜져 있어야 합니다.)

> 완전한 오프라인 단독 앱(폰이 스스로 음성 인식)은 폰 성능·모델 크기 때문에
> 현재 범위 밖입니다. 위 방식은 PC의 성능을 그대로 쓰는 가장 안전·정확한 길이에요.

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
