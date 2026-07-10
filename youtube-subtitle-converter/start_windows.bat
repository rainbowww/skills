@echo off
chcp 65001 >nul
REM Target: Windows - double-click this file in Explorer (no PowerShell needed).
REM ASCII-only launcher. First run creates a venv and installs deps (a few min);
REM after that it just starts the web app. Korean messages come from Python.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not installed.
  echo         Install it from https://www.python.org/downloads/ and run again.
  echo         IMPORTANT: tick "Add python.exe to PATH" during install.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] First run: creating virtual environment ...
  python -m venv .venv
  echo [2/3] Installing required packages ... (may take a few minutes)
  .venv\Scripts\python -m pip install --quiet --upgrade pip
  .venv\Scripts\python -m pip install --quiet -r requirements.txt
)

REM check-then-run: only launch if the app entry file exists
if not exist "app.py" (
  echo [ERROR] app.py not found in this folder. Re-download the package.
  pause
  exit /b 1
)

echo [3/3] Starting Subtitle Converter. Your browser will open http://127.0.0.1:5123
start "" http://127.0.0.1:5123
.venv\Scripts\python app.py
pause
