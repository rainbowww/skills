#!/usr/bin/env bash
# 스킬 내보내기 — Linux / macOS / Windows(Git Bash·WSL)
# 사용법: bash export.sh  →  상위 폴더에 portable-ai-setup_Ver{N}.zip 생성
# 버전은 VERSION 파일이 결정한다. 파일명에 항상 버전이 붙는다 (혼동 방지 규칙).
set -euo pipefail
cd "$(dirname "$0")"
VER="$(tr -d '[:space:]' < VERSION)"
[ -n "$VER" ] || { echo "오류: VERSION 파일이 비어 있음"; exit 1; }
OUT="../portable-ai-setup_Ver${VER}.zip"
rm -f "$OUT"
if command -v zip >/dev/null 2>&1; then
  zip -r "$OUT" . -x "*.zip"
else
  OUT="../portable-ai-setup_Ver${VER}.tar.gz"
  tar -czf "$OUT" .
fi
echo "내보내기 완료: $OUT  (버전 ${VER})"
echo "배포 전 체크: 내용 수정했다면 VERSION 숫자를 올렸는가?"
