#!/usr/bin/env bash
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 (WSL 포함) — bash start.sh
# 설명: 처음 실행 시 가상환경 생성+설치(수 분), 이후엔 바로 웹앱 실행
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null; then
  echo "[오류] python3가 없습니다. 먼저 설치하세요."; exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "[1/3] 처음 실행: 가상환경 생성 중..."
  python3 -m venv .venv
  echo "[2/3] 필요한 프로그램 설치 중... (수 분 걸릴 수 있어요)"
  .venv/bin/pip install --quiet --upgrade pip
  .venv/bin/pip install --quiet -r requirements.txt
fi

echo "[3/3] 자막 변환기 실행! 브라우저에서 http://127.0.0.1:5123 을 여세요. (종료: Ctrl+C)"
.venv/bin/python app.py
