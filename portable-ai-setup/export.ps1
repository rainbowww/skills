# Skill export - PowerShell (Windows / macOS / Linux). ASCII-only launcher.
# Usage: .\export.ps1   (if blocked on a shared PC: powershell -ExecutionPolicy Bypass -File .\export.ps1)
# The VERSION file decides the version. The version is always in the filename (anti-confusion rule).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$ver = (Get-Content (Join-Path $PSScriptRoot "VERSION") -Raw).Trim()
if (-not $ver) { throw "ERROR: VERSION file is empty" }
$out = Join-Path (Split-Path $PSScriptRoot -Parent) "portable-ai-setup_Ver$ver.zip"
if (Test-Path $out) { Remove-Item $out }
$src = Join-Path $PSScriptRoot "*"
Compress-Archive -Path $src -DestinationPath $out
Write-Host "Export complete: $out  (version $ver)"
Write-Host "Pre-release check: if you changed content, did you bump the VERSION number?"
