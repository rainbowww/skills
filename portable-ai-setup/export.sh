#!/usr/bin/env bash
# 스킬 내보내기 — Linux / macOS / Windows(Git Bash·WSL)
# 사용법: bash export.sh  →  상위 폴더에 portable-ai-setup.zip 생성
set -euo pipefail
cd "$(dirname "$0")"
OUT="../portable-ai-setup.zip"
rm -f "$OUT"
if command -v zip >/dev/null 2>&1; then
  zip -r "$OUT" . -x "*.zip"
else
  # zip이 없는 환경(일부 리눅스 최소설치) 대비
  tar -czf "../portable-ai-setup.tar.gz" .
  OUT="../portable-ai-setup.tar.gz"
fi
echo "내보내기 완료: $OUT"
echo "USB/메일/클라우드로 옮긴 뒤 압축 해제하면 어느 장소에서든 동일하게 사용."
