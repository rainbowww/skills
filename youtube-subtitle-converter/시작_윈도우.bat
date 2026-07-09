@echo off
REM 대상(실행 위치): 🟦 Windows — 탐색기에서 이 파일을 더블클릭 (PowerShell 불필요)
REM 설명: 처음 실행 시 가상환경 생성+설치(수 분), 이후엔 바로 웹앱 실행
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [오류] Python이 설치되어 있지 않습니다.
  echo        https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요.
  echo        ※ 설치 시 "Add python.exe to PATH" 체크 필수
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] 처음 실행: 가상환경 생성 중...
  python -m venv .venv
  echo [2/3] 필요한 프로그램 설치 중... ^(수 분 걸릴 수 있어요^)
  .venv\Scripts\python -m pip install --quiet --upgrade pip
  .venv\Scripts\python -m pip install --quiet -r requirements.txt
)

echo [3/3] 자막 변환기 실행! 잠시 후 브라우저에서 http://127.0.0.1:5123 을 여세요.
start "" http://127.0.0.1:5123
.venv\Scripts\python app.py
pause
