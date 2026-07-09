# 스킬 내보내기 — PowerShell (Windows / macOS / Linux 공용)
# 사용법: .\export.ps1   (공용 PC에서 차단 시: powershell -ExecutionPolicy Bypass -File .\export.ps1)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$out = Join-Path (Split-Path $PSScriptRoot -Parent) "portable-ai-setup.zip"
if (Test-Path $out) { Remove-Item $out }
$src = Join-Path $PSScriptRoot "*"
Compress-Archive -Path $src -DestinationPath $out
Write-Host "내보내기 완료: $out"
Write-Host "USB/메일/클라우드로 옮긴 뒤 압축 해제하면 어느 장소에서든 동일하게 사용."
