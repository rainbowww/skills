@echo off
REM 대상(실행 위치): 🟦 Windows — 더블클릭 또는 cmd에서 실행 (PowerShell·WSL 미사용)
REM 역할: 진입점. 파이썬 없으면 자동 설치 유도(winget) → 공용 oneshot.py 내려받아 실행 → 콘솔 유지.
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
set "DEST=%USERPROFILE%\youtube-subtitle-converter"
set "RAW=https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"

echo ============================================================
echo   자막 변환기 원샷 설치 (Windows 전용, WSL 불필요)
echo ============================================================

REM ---- [선행1] curl 확인 (Windows 10 1803+ 내장) ----
where curl >nul 2>nul
if errorlevel 1 (
  echo [오류] 이 Windows에는 curl이 없습니다(구버전).
  echo        Windows 10 이상으로 업데이트하거나, 브라우저로 아래를 내려받아 실행하세요:
  echo        %RAW%/install.bat
  echo.
  pause
  exit /b 1
)

REM ---- [선행2] 파이썬 있음/없음 판정 → 있으면 통과, 없으면 자동 설치 ----
set "PYCMD="
where python >nul 2>nul && set "PYCMD=python"
if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )

if not defined PYCMD (
  echo [..] Python이 없어 자동 설치를 시도합니다 (winget)...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo [안내] 자동 설치 도구(winget)가 없습니다.
    echo        https://www.python.org/downloads/ 에서 Python을 설치하세요.
    echo        ※ 설치 첫 화면 "Add python.exe to PATH" 체크 필수. 설치 후 이 파일을 다시 더블클릭하세요.
    echo.
    pause
    exit /b 1
  )
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
  REM winget 설치 후 현재 창은 PATH가 갱신되지 않을 수 있음 → 한 번만 다시 실행 안내
  where python >nul 2>nul && set "PYCMD=python"
  if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )
  if not defined PYCMD (
    echo.
    echo [완료] Python 설치가 끝났습니다. PATH 적용을 위해 이 파일 ^(install.bat^)을
    echo        한 번만 다시 더블클릭해 주세요. 그러면 바로 이어서 진행됩니다.
    echo.
    pause
    exit /b 0
  )
)
echo [OK] Python 확인됨 (%PYCMD%).

if not exist "%DEST%" mkdir "%DEST%"

REM ---- oneshot.py 내려받기 (재시도 포함) ----
echo [..] 설치 엔진(oneshot.py) 내려받는 중...
curl -fsSL --retry 4 --retry-delay 2 "%RAW%/oneshot.py" -o "%DEST%\oneshot.py"
if errorlevel 1 (
  echo [오류] oneshot.py 다운로드 실패. 인터넷 연결을 확인하세요.
  echo.
  pause
  exit /b 1
)

REM ---- 공용 엔진 실행 (환경조사/설치/검증/결과기록 모두 파이썬이 수행) ----
%PYCMD% "%DEST%\oneshot.py"
set "RC=%errorlevel%"

echo.
echo ------------------------------------------------------------
if "%RC%"=="0" (
  echo 결과: 성공 ^(PASS^)  ^|  로그/결과: %DEST%\.oneshot\
  echo 브라우저에서 http://127.0.0.1:5123 을 여세요.
) else (
  echo 결과: 실패 ^(코드 %RC%^)  ^|  원인/로그: %DEST%\.oneshot\install.log
)
echo ------------------------------------------------------------
pause
exit /b %RC%
