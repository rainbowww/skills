# 대상(실행 위치): 🟦 Windows PowerShell — 한 줄 실행(원샷):
#   irm https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.ps1 | iex
# 역할: 진입점만. python 확인/자동설치(winget) → 공용 oneshot.py 내려받아 실행.
# (실제 환경조사·설치·검증·결과기록은 모두 oneshot.py가 수행 — install.bat / install.sh 와 동일 엔진)
$ErrorActionPreference = "Stop"
$RAW  = "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"
$DEST = Join-Path $env:USERPROFILE "youtube-subtitle-converter"

function Box($m) { Write-Host " $m " -ForegroundColor Black -BackgroundColor White }
function Danger($m) { Write-Host " $m " -ForegroundColor White -BackgroundColor Red }

Box "자막 변환기 원샷 설치 (Windows PowerShell)"

# [선행] python 있음/없음 판정 — 있으면 통과, 없으면 winget 자동설치 시도
$py = $null
foreach ($c in @("python", "py")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
  Box "Python이 없어 자동 설치를 시도합니다 (winget)..."
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
    # winget 설치 후 현재 세션 PATH가 갱신 안 될 수 있음 → 재탐색
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    foreach ($c in @("python", "py")) {
      if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
    }
  }
}
if (-not $py) {
  Danger "Python을 찾을 수 없습니다. https://www.python.org/downloads/ 에서 설치하세요."
  Write-Host '   ※ 설치 첫 화면 "Add python.exe to PATH" 체크 필수. 설치 후 이 명령을 다시 실행하세요.'
  exit 1
}
Write-Host "[OK] Python 확인됨 ($py)."

New-Item -ItemType Directory -Force -Path $DEST | Out-Null

# oneshot.py 내려받기 (curl.exe: PowerShell의 curl 별명 회피)
Box "설치 엔진(oneshot.py) 내려받는 중..."
& curl.exe -fsSL --retry 4 --retry-delay 2 "$RAW/oneshot.py" -o (Join-Path $DEST "oneshot.py")
if ($LASTEXITCODE -ne 0 -or -not (Test-Path (Join-Path $DEST "oneshot.py"))) {
  Danger "oneshot.py 다운로드 실패 — 인터넷 연결을 확인하세요."
  exit 1
}

# 공용 엔진 실행 (환경조사/설치/검증/결과기록 모두 파이썬이 수행)
& $py (Join-Path $DEST "oneshot.py")
$rc = $LASTEXITCODE

Write-Host "------------------------------------------------------------"
if ($rc -eq 0) {
  Write-Host "결과: 성공 (PASS)  |  브라우저에서 http://127.0.0.1:5123 을 여세요."
} else {
  Danger "결과: 실패 (코드 $rc)  |  원인/로그: $DEST\.oneshot\install.log"
}
exit $rc
