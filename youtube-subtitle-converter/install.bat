@echo off
REM 대상(실행 위치): 🟦 Windows — 이 파일을 더블클릭 (PowerShell 미사용 원칙)
REM 역할: 진입점만 담당. 파이썬 확인 → 공용 oneshot.py 내려받아 실행 → 콘솔 유지.
setlocal EnableExtensions
chcp 65001 >nul
set "DEST=%USERPROFILE%\youtube-subtitle-converter"
set "RAW=https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"

echo ============================================================
echo   자막 변환기 원샷 설치 (Windows)
echo ============================================================

REM [선행] 파이썬 있는지 없는지 판정 — 있으면 통과, 없으면 안내 후 종료
where python >nul 2>nul
if errorlevel 1 (
  echo [오류] Python이 설치되어 있지 않습니다.
  echo        https://www.python.org/downloads/ 에서 설치하세요.
  echo        ※ 설치 첫 화면에서 "Add python.exe to PATH" 체크는 필수입니다.
  echo.
  pause
  exit /b 1
)
echo [OK] Python 확인됨.

if not exist "%DEST%" mkdir "%DEST%"

REM oneshot.py 내려받기 (curl은 Windows 10 1803+ 내장 — PowerShell 불필요)
echo [..] 설치 엔진(oneshot.py) 내려받는 중...
curl -fsSL --retry 4 --retry-delay 2 "%RAW%/oneshot.py" -o "%DEST%\oneshot.py"
if errorlevel 1 (
  echo [오류] oneshot.py 다운로드 실패. 인터넷 연결을 확인하세요.
  echo.
  pause
  exit /b 1
)

REM 공용 엔진 실행 (환경조사/설치/검증/결과기록은 모두 파이썬이 수행)
python "%DEST%\oneshot.py"
set "RC=%errorlevel%"

echo.
echo ------------------------------------------------------------
if "%RC%"=="0" (
  echo 결과: 성공(PASS)  ^|  로그/결과: %DEST%\.oneshot\
) else (
  echo 결과: 실패(코드 %RC%)  ^|  원인/로그: %DEST%\.oneshot\install.log
)
echo ------------------------------------------------------------
pause
exit /b %RC%
