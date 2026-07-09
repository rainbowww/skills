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
  "prompts/claudeai-instructions.md", "prompts/PASTE-claude-ai.txt",
  "templates/CLAUDE.md.template",
  "locations/A-company.md", "locations/B-home.md", "locations/C-school.md"
)

# 1) 살아있는 브랜치 탐색
$base = $null
foreach ($b in $branches) {
  try {
    # [string] 캐스팅 필수: 숫자만 있는 VERSION을 irm이 Int64로 파싱해 .Trim()이 없어 죽는 버그 방지
    $v = ([string](Invoke-RestMethod "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup/VERSION")).Trim()
    $base = "https://raw.githubusercontent.com/$repo/$b/portable-ai-setup"
    break
  } catch { continue }
}
if (-not $base) { Danger "GitHub에서 패키지를 찾지 못했습니다. 인터넷 연결을 확인하세요."; exit 1 }

# 2) 버전 폴더에 설치 (버전별 분리 = 혼동 원천 차단)
$dest = Join-Path $HOME "portable-ai-setup_Ver$v"
New-Item -ItemType Directory -Force -Path $dest, "$dest/prompts", "$dest/templates", "$dest/locations" | Out-Null
foreach ($f in $files) {
  # 429(요청 과다) 등 일시 오류 대비: 최대 4회 재시도, 점증 대기
  $ok = $false
  for ($try = 1; $try -le 4; $try++) {
    try {
      Invoke-WebRequest "$base/$f" -OutFile (Join-Path $dest $f) -UseBasicParsing
      $ok = $true; break
    } catch {
      if ($try -lt 4) { Start-Sleep -Seconds ($try * 3) }
    }
  }
  if (-not $ok) { Danger "다운로드 실패: $f — 잠시 후 다시 실행하세요."; exit 1 }
  Start-Sleep -Milliseconds 300  # 연속 요청 간격(레이트리밋 예방)
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

# 4) 완료 안내 + 복붙 전용 파일 자동 열기 (내용 전체가 붙여넣을 것 — 고를 필요 없음)
Write-Host ""
Info "설치 완료: 버전 $v  →  $dest"
Info "지금 열리는 파일에서 Ctrl+A(전체선택) → Ctrl+C(복사) → AI 도구 지침란에 붙여넣기. 그게 전부."
Warn "공용 PC라면 사용 후 폴더 삭제: Remove-Item -Recurse '$dest'"
# notepad는 Windows 전용 — 맥/리눅스 pwsh에서는 경로만 안내
if ($env:OS -eq "Windows_NT") {
  Start-Process notepad (Join-Path $dest "prompts/PASTE-claude-ai.txt")
} else {
  Info "복붙 전용 파일: $(Join-Path $dest 'prompts/PASTE-claude-ai.txt')"
}
