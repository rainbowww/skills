# Target: Windows PowerShell. One-line run:
#   irm https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.ps1 | iex
# Thin entry point only. ASCII-only on purpose (Windows PowerShell 5.1 reads a
# saved .ps1 as ANSI/CP949 without a BOM -> Korean would break). Korean user
# messages live in oneshot.py (Python prints Unicode safely). This launcher:
#   ensure Python (winget) -> download oneshot.py -> VERIFY it exists -> run it.
$ErrorActionPreference = "Stop"
$RAW  = "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"
$DEST = Join-Path $env:USERPROFILE "youtube-subtitle-converter"

function Box($m) { Write-Host " $m " -ForegroundColor Black -BackgroundColor White }
function Danger($m) { Write-Host " $m " -ForegroundColor White -BackgroundColor Red }

Box "Subtitle Converter - one-shot installer (Windows PowerShell)"

# [1] Python present? if not, try winget auto-install
$py = $null
foreach ($c in @("python", "py")) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
  Box "Python not found. Trying auto-install via winget ..."
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    foreach ($c in @("python", "py")) {
      if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
    }
  }
}
if (-not $py) {
  Danger "Python not found. Install it from https://www.python.org/downloads/"
  Write-Host '   IMPORTANT: tick "Add python.exe to PATH", then run this command again.'
  return
}
Write-Host "[OK] Python found ($py)."

New-Item -ItemType Directory -Force -Path $DEST | Out-Null

# [2] download shared engine with curl.exe (avoids the PowerShell curl alias)
Box "Downloading install engine (oneshot.py) ..."
$engine = Join-Path $DEST "oneshot.py"
if (Test-Path $engine) { Remove-Item $engine -Force }
& curl.exe -fsSL --retry 4 --retry-delay 2 "$RAW/oneshot.py" -o $engine

# [3] VERIFY the file exists and is non-empty BEFORE running it (check-then-run)
if (-not (Test-Path $engine) -or ((Get-Item $engine).Length -lt 100)) {
  Danger "Download failed or file is incomplete. Not running. Check your internet connection."
  return
}
Write-Host ("[OK] oneshot.py downloaded ({0} bytes)." -f (Get-Item $engine).Length)

# [4] run shared engine (survey / deps install / verify / results; Korean output from Python)
& $py $engine
$rc = $LASTEXITCODE

Write-Host "------------------------------------------------------------"
if ($rc -eq 0) {
  Write-Host "RESULT: PASS  |  Open http://127.0.0.1:5123 in your browser."
} else {
  Danger "RESULT: FAIL (code $rc)  |  log: $DEST\.oneshot\install.log"
}
