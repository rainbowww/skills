# 스킬 내보내기 — Windows PowerShell
# 사용법: PowerShell에서  .\export.ps1  실행  →  상위 폴더에 portable-ai-setup.zip 생성
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$out = Join-Path (Split-Path $PSScriptRoot -Parent) "portable-ai-setup.zip"
if (Test-Path $out) { Remove-Item $out }
Compress-Archive -Path "$PSScriptRoot\*" -DestinationPath $out
Write-Host "내보내기 완료: $out"
Write-Host "USB/메일/클라우드로 옮긴 뒤 압축 해제하면 어느 장소에서든 동일하게 사용."
