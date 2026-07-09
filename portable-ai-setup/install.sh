#!/usr/bin/env bash
# 원샷 설치기 — macOS / Linux (한 줄 실행용)
# 사용법:
#   curl -sSL https://raw.githubusercontent.com/rainbowww/skills/main/portable-ai-setup/install.sh | bash
# 실행하면: GitHub에서 최신 버전 자동 다운로드 → 설치 → Claude Code 설정 적용 → 경로 안내
set -euo pipefail

# 색상 안내 박스: 안내=흰배경, 경고=노란배경, 위험=빨간배경
info()   { printf '\033[47;30m %s \033[0m\n' "$1"; }
warn()   { printf '\033[43;30m %s \033[0m\n' "$1"; }
danger() { printf '\033[41;97m %s \033[0m\n' "$1"; }

REPO="rainbowww/skills"
BRANCHES=("main" "claude/claude-md-docs-8r1kk7")
FILES=(VERSION SKILL.md README.md export.sh export.ps1 install.sh install.ps1
  prompts/universal-system-prompt.md prompts/final-work-instruction.md
  prompts/claudeai-instructions.md prompts/PASTE-claude-ai.txt
  templates/CLAUDE.md.template
  locations/A-company.md locations/B-home.md locations/C-school.md)

BASE=""
for b in "${BRANCHES[@]}"; do
  if V=$(curl -fsSL "https://raw.githubusercontent.com/$REPO/$b/portable-ai-setup/VERSION" 2>/dev/null | tr -d '[:space:]'); then
    BASE="https://raw.githubusercontent.com/$REPO/$b/portable-ai-setup"
    break
  fi
done
[ -n "$BASE" ] || { danger "GitHub에서 패키지를 찾지 못했습니다. 인터넷 연결을 확인하세요."; exit 1; }

DEST="$HOME/portable-ai-setup_Ver$V"
mkdir -p "$DEST"/{prompts,templates,locations}
for f in "${FILES[@]}"; do
  # 429(요청 과다) 등 일시 오류 대비: 최대 4회 재시도, 점증 대기 + 요청 간격
  curl -fsSL --retry 4 --retry-delay 3 --retry-all-errors "$BASE/$f" -o "$DEST/$f" \
    || { danger "다운로드 실패: $f — 잠시 후 다시 실행하세요."; exit 1; }
  sleep 0.3
done

# Claude Code 반자동 설정 (설정 파일이 없을 때만 생성 — 기존 설정 보호)
CC="$HOME/.claude/settings.json"
if [ ! -f "$CC" ]; then
  mkdir -p "$HOME/.claude"
  printf '{ "permissions": { "defaultMode": "acceptEdits" } }\n' > "$CC"
  # 재시작 필요 여부 자동 판정: 실행 중이면 재시작 필요, 아니면 다음 실행 시 자동 로드
  if pgrep -f "claude" >/dev/null 2>&1; then
    warn "Claude Code가 실행 중입니다 — 재시작해야 반자동 설정이 적용됩니다."
  else
    info "Claude Code 반자동 설정 완료 — 재시작 불필요, 다음 실행 시 자동 로드됩니다."
  fi
else
  info "Claude Code 설정이 이미 있어 건드리지 않았습니다. 반자동 전환은 Claude Code에서 Shift+Tab."
fi

echo ""
info "설치 완료: 버전 $V  →  $DEST"
info "복붙 전용 파일(전체선택→복사→붙여넣기, 고를 필요 없음): $DEST/prompts/PASTE-claude-ai.txt"
warn "공용 PC라면 사용 후 삭제: rm -rf '$DEST'"
