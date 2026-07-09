# 스킬 내보내기 — PowerShell (Windows / macOS / Linux 공용)
# 사용법: .\export.ps1   (공용 PC에서 차단 시: powershell -ExecutionPolicy Bypass -File .\export.ps1)
# 버전은 VERSION 파일이 결정한다. 파일명에 항상 버전이 붙는다 (혼동 방지 규칙).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$ver = (Get-Content (Join-Path $PSScriptRoot "VERSION") -Raw).Trim()
if (-not $ver) { throw "오류: VERSION 파일이 비어 있음" }
$out = Join-Path (Split-Path $PSScriptRoot -Parent) "portable-ai-setup_Ver$ver.zip"
if (Test-Path $out) { Remove-Item $out }
$src = Join-Path $PSScriptRoot "*"
Compress-Archive -Path $src -DestinationPath $out
Write-Host "내보내기 완료: $out  (버전 $ver)"
Write-Host "배포 전 체크: 내용 수정했다면 VERSION 숫자를 올렸는가?"
