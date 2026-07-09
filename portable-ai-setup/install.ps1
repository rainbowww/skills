# 원샷 설치기 — Windows PowerShell (한 줄 실행용)
# 사용법(관리자 불필요):
#   irm https://raw.githubusercontent.com/rainbowww/skills/main/portable-ai-setup/install.ps1 | iex
# 실행하면: GitHub에서 최신 버전 자동 다운로드 → 설치 → Claude Code 설정 적용 → 프롬프트 파일 자동 열기
$ErrorActionPreference = "Stop"

# 색상 안내 박스: 안내=흰배경, 경고=노란배경, 위험=빨간배경
function Info($m)   { Write-Host " $m " -BackgroundColor White  -ForegroundColor Black }
function Warn($m)   { Write-Host " $m " -BackgroundColor Yellow -ForegroundColor Black }
function Danger($m) { Write-Host " $m " -BackgroundColor Red    -ForegroundColor White }

$repo = "rainbowww/skills"
$branches = @("main", "claude/claude-md-docs-8r1kk7")  # main 우선, 머지 전이면 작업 브랜치
$files = @(
  "VERSION", "SKILL.md", "README.md", "export.sh", "export.ps1",
  "install.sh", "install.ps1",
  "prompts/universal-system-prompt.md", "prompts/final-work-instruction.md",
  "templates/CLAUDE.md.template",
  "locations/A-company.md", "locations/B-home.md", "locations/C-school.md"
)

# 1) 살아있는 브랜치 탐색
$base = $null
foreach ($b in $branches) {
  try {
    $v = (Invoke-RestMethod "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup/VERSION").Trim()
    $base = "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup"
    break
  } catch { continue }
}
if (-not $base) { Danger "GitHub에서 패키지를 찾지 못했습니다. 인터넷 연결을 확인하세요."; exit 1 }

# 2) 버전 폴더에 설치 (버전별 분리 = 혼동 원천 차단)
$dest = Join-Path $HOME "portable-ai-setup_Ver$v"
New-Item -ItemType Directory -Force -Path $dest, "$dest/prompts", "$dest/templates", "$dest/locations" | Out-Null
foreach ($f in $files) {
  Invoke-WebRequest "$base/$f" -OutFile (Join-Path $dest $f) -UseBasicParsing
}

# 3) Claude Code 반자동 설정 (설정 파일이 없을 때만 생성 — 기존 설정 보호)
$ccDir = Join-Path $HOME ".claude"
$ccSettings = Join-Path $ccDir "settings.json"
if (-not (Test-Path $ccSettings)) {
  New-Item -ItemType Directory -Force -Path $ccDir | Out-Null
  '{ "permissions": { "defaultMode": "acceptEdits" } }' | Set-Content $ccSettings -Encoding UTF8
  # 재시작 필요 여부 자동 판정: 실행 중이면 재시작 필요, 아니면 다음 실행 시 자동 로드
  $running = Get-Process -Name "claude*" -ErrorAction SilentlyContinue
  if ($running) { Warn "Claude Code가 실행 중입니다 — 재시작해야 반자동 설정이 적용됩니다." }
  else          { Info "Claude Code 반자동 설정 완료 — 재시작 불필요, 다음 실행 시 자동 로드됩니다." }
} else {
  Info "Claude Code 설정이 이미 있어 건드리지 않았습니다. 반자동 전환은 Claude Code에서 Shift+Tab."
}

# 4) 완료 안내 + 프롬프트 파일 자동 열기
Write-Host ""
Info "설치 완료: 버전 $v  →  $dest"
Info "지금 열리는 파일에서 [B절 코드블록]을 복사해 AI 도구에 붙여넣으면 끝."
Warn "공용 PC라면 사용 후 폴더 삭제: Remove-Item -Recurse '$dest'"
Start-Process notepad (Join-Path $dest "prompts/universal-system-prompt.md")
