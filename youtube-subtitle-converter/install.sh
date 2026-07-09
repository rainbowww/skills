#!/usr/bin/env bash
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 또는 WSL — 대표 진입점(원샷). 한 줄:
#   curl -sSL https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.sh | bash
# 역할: 진입점만. python3 확인/자동설치 → 공용 oneshot.py 내려받아 실행.
# (실제 환경조사·설치·검증·결과기록은 모두 oneshot.py가 수행 — Windows와 동일 파일)
set -uo pipefail
DEST="$HOME/youtube-subtitle-converter"
RAW="https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"
mkdir -p "$DEST"

box(){ printf '\033[47;30m %s \033[0m\n' "$1"; }

# [선행] python3 있는지 없는지 판정 — 있으면 통과, 없으면 자동설치 시도
if ! command -v python3 >/dev/null; then
  box "python3가 없어 자동 설치를 시도합니다..."
  PKGS="python3 python3-venv python3-pip"
  if   command -v apt-get >/dev/null; then CMD="apt-get update -qq && apt-get install -y -qq $PKGS"
  elif command -v dnf     >/dev/null; then CMD="dnf install -y -q $PKGS"
  elif command -v yum     >/dev/null; then CMD="yum install -y -q $PKGS"
  elif command -v apk     >/dev/null; then CMD="apk add --no-progress $PKGS"
  elif command -v brew    >/dev/null; then CMD="brew install python"
  else CMD=""; fi
  if   [ -z "$CMD" ]; then :
  elif [ "$(id -u)" = "0" ]; then eval "$CMD" || true
  elif sudo -n true 2>/dev/null; then eval "sudo $CMD" || true; fi
fi
if ! command -v python3 >/dev/null; then
  printf '\033[41;97m python3를 찾을 수 없습니다. 한 번만: sudo apt install -y python3 python3-venv python3-pip \033[0m\n'
  exit 1
fi

box "설치 엔진(oneshot.py) 내려받는 중..."
curl -fsSL --retry 4 --retry-delay 2 --retry-all-errors "$RAW/oneshot.py" -o "$DEST/oneshot.py" \
  || { printf '\033[41;97m oneshot.py 다운로드 실패 — 인터넷 확인 \033[0m\n'; exit 1; }

exec python3 "$DEST/oneshot.py"
