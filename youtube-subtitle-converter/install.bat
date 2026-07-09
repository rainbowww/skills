@echo off
chcp 65001 >nul
REM Target: Windows (double-click or cmd). No PowerShell / no WSL.
REM Thin entry point only. This file is ASCII-only ON PURPOSE:
REM   Korean text inside a .bat breaks on Korean Windows (CP949) and gets
REM   mis-parsed as commands. All Korean user messages live in oneshot.py
REM   (Python prints Unicode safely). This launcher just: check curl ->
REM   ensure Python (winget) -> download oneshot.py -> run it.
setlocal EnableExtensions EnableDelayedExpansion
set "DEST=%USERPROFILE%\youtube-subtitle-converter"
set "RAW=https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"

echo ============================================================
echo   Subtitle Converter - one-shot installer (Windows)
echo ============================================================

REM ---- [1] curl (built into Windows 10 1803+) ----
where curl >nul 2>nul
if errorlevel 1 (
  echo [ERROR] curl not found. Update to Windows 10+ , or download this file
  echo         with a browser from:
  echo         %RAW%/install.bat
  echo.
  pause
  exit /b 1
)

REM ---- [2] Python present? if not, auto-install via winget ----
set "PYCMD="
where python >nul 2>nul && set "PYCMD=python"
if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )

if not defined PYCMD (
  echo [..] Python not found. Trying auto-install via winget ...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo [INFO] winget is not available on this PC.
    echo        Install Python from https://www.python.org/downloads/
    echo        IMPORTANT: tick "Add python.exe to PATH" on the first screen,
    echo        then double-click this file again.
    echo.
    pause
    exit /b 1
  )
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
  where python >nul 2>nul && set "PYCMD=python"
  if not defined PYCMD ( where py >nul 2>nul && set "PYCMD=py" )
  if not defined PYCMD (
    echo.
    echo [DONE] Python installed. Please double-click install.bat ONE more time
    echo        so the new PATH is picked up. It will continue automatically.
    echo.
    pause
    exit /b 0
  )
)
echo [OK] Python found (%PYCMD%).

if not exist "%DEST%" mkdir "%DEST%"

REM ---- [3] download shared engine (retry included) ----
echo [..] Downloading install engine (oneshot.py) ...
curl -fsSL --retry 4 --retry-delay 2 "%RAW%/oneshot.py" -o "%DEST%\oneshot.py"
if errorlevel 1 (
  echo [ERROR] Failed to download oneshot.py. Check your internet connection.
  echo.
  pause
  exit /b 1
)

REM ---- check-then-run: verify file EXISTS and is non-empty BEFORE executing ----
if not exist "%DEST%\oneshot.py" (
  echo [ERROR] oneshot.py was not saved. Not running.
  echo.
  pause
  exit /b 1
)
for %%A in ("%DEST%\oneshot.py") do if %%~zA LSS 100 (
  echo [ERROR] oneshot.py is incomplete (%%~zA bytes). Not running.
  echo.
  pause
  exit /b 1
)

REM ---- [4] run shared engine: survey / deps install / verify / results ----
REM (This is where Korean progress messages appear - printed by Python.)
%PYCMD% "%DEST%\oneshot.py"
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
