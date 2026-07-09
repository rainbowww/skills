@echo off
chcp 65001 >nul
REM Target: Windows - works from double-click, cmd, OR PowerShell (.\install.bat).
REM ONE launcher for every Windows version (no separate .ps1). ASCII-only on
REM purpose: Korean text inside a .bat breaks on Korean Windows (CP949).
REM This file does ONLY the prerequisite ("contact point"): make sure Python
REM exists, then download oneshot.py. Everything after - install, verify, run,
REM and all Korean messages - is managed by Python (oneshot.py).
setlocal EnableExtensions EnableDelayedExpansion
set "DEST=%USERPROFILE%\youtube-subtitle-converter"
set "RAW=https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"

echo ============================================================
echo   Subtitle Converter - one-shot installer (Windows)
echo ============================================================

REM ---- [1] ensure Python (the contact point). missing -> winget, else guide ----
set "PYCMD="
where python >nul 2>nul && set "PYCMD=python"
if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )
if not defined PYCMD (
  echo [..] Python not found. Trying auto-install via winget ...
  where winget >nul 2>nul && (
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
    where python >nul 2>nul && set "PYCMD=python"
    if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )
  )
)
if not defined PYCMD (
  echo [INFO] Could not set up Python automatically on this Windows version.
  echo        Install Python from https://www.python.org/downloads/
  echo        IMPORTANT: tick "Add python.exe to PATH" on the first screen,
  echo        then run this file again. It will continue automatically.
  echo.
  pause
  exit /b 1
)
echo [OK] Python found (%PYCMD%).

if not exist "%DEST%" mkdir "%DEST%"

REM ---- [2] download shared engine oneshot.py (compatible with old + new) ----
REM   new Windows (10 1803+): curl. old Windows (no curl): PowerShell + TLS 1.2
REM   (GitHub requires TLS 1.2; old .NET defaults to TLS 1.0 and would fail).
echo [..] Downloading install engine (oneshot.py) ...
set "ENGINE=%DEST%\oneshot.py"
if exist "%ENGINE%" del /q "%ENGINE%" >nul 2>nul
where curl >nul 2>nul && curl -fsSL --retry 4 --retry-delay 2 "%RAW%/oneshot.py" -o "%ENGINE%"
if not exist "%ENGINE%" powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%RAW%/oneshot.py' -OutFile '%ENGINE%'" 2>nul

REM ---- check-then-run: verify the file EXISTS and is non-empty BEFORE running ----
if not exist "%ENGINE%" (
  echo [ERROR] Failed to download oneshot.py. Check your internet connection,
  echo         or download this file with a browser and run it again:
  echo         %RAW%/install.bat
  echo.
  pause
  exit /b 1
)
for %%A in ("%ENGINE%") do if %%~zA LSS 100 (
  echo [ERROR] oneshot.py is incomplete (%%~zA bytes). Not running.
  echo.
  pause
  exit /b 1
)

REM ---- [3] hand off to Python. Python manages everything from here on. ----
REM (This is where Korean progress messages appear - printed by Python.)
%PYCMD% "%ENGINE%"
set "RC=%errorlevel%"

echo.
echo ------------------------------------------------------------
if "%RC%"=="0" (
  echo RESULT: PASS  ^|  logs: %DEST%\.oneshot\
  echo Open http://127.0.0.1:5123 in your browser.
) else (
  echo RESULT: FAIL ^(code %RC%^)  ^|  log: %DEST%\.oneshot\install.log
)
echo ------------------------------------------------------------
pause
exit /b %RC%
