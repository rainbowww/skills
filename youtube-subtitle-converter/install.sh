#!/usr/bin/env bash
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 또는 WSL — 대표 진입점(원샷). 한 줄:
#   curl -sSL https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter/install.sh | bash
# 역할(윈도우 install.bat과 동일 구조): '인도(선행과제)'만 맡는다 —
#   python3 확인/자동설치 → 공용 oneshot.py 내려받기 = '접점'까지.
#   그 다음(환경조사·설치·검증·실행·결과기록·한글 안내)은 모두 oneshot.py(파이썬)가 관리.
set -uo pipefail
DEST="$HOME/youtube-subtitle-converter"
RAW="https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/youtube-subtitle-converter"
mkdir -p "$DEST"

box(){ printf '\033[47;30m %s \033[0m\n' "$1"; }
danger(){ printf '\033[41;97m %s \033[0m\n' "$1"; }

# [선행] python3 있는지 판정 — 있으면 통과, 없으면 배포판별 자동설치 시도
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
  danger "python3를 찾을 수 없습니다. 한 번만: sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi

# [접점] 공용 엔진 oneshot.py 내려받기 — curl 우선, 없으면 wget 폴백(맥=curl, 일부 리눅스=wget)
box "설치 엔진(oneshot.py) 내려받는 중..."
ENGINE="$DEST/oneshot.py"
rm -f "$ENGINE"
if   command -v curl >/dev/null; then
  curl -fsSL --retry 4 --retry-delay 2 --retry-all-errors "$RAW/oneshot.py" -o "$ENGINE" || true
elif command -v wget >/dev/null; then
  wget -q --tries=4 -O "$ENGINE" "$RAW/oneshot.py" || true
else
  danger "curl 또는 wget이 필요합니다. 한 번만: sudo apt install -y curl"
  exit 1
fi

# check-then-run: 파일이 실제로 있고 충분히 큰지 확인한 뒤에만 실행
if [ ! -s "$ENGINE" ] || [ "$(wc -c < "$ENGINE")" -lt 100 ]; then
  danger "oneshot.py 다운로드 실패/불완전 — 인터넷 연결을 확인하세요."
  exit 1
fi

# 여기서부터 파이썬이 전부 관리한다(윈도우와 동일한 공용 파일).
exec python3 "$ENGINE"
