#!/usr/bin/env bash
# HERMES 콘솔(node server.js 18091)의 HTML에 복사/붙여넣기 버튼을 넣는다.
# 안전 원칙: ① 백업 먼저 ② 삽입 후 콘솔이 안 뜨면 '자동 원상복구'. 절대 콘솔을 죽은 채 두지 않는다.
set -u

INJ_URL="https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/hermes-console/inject.html"

P=$(pgrep -f "server.js 18091" | head -1)
[ -z "${P:-}" ] && { echo "결과=콘솔 서버(server.js 18091)가 이 노드에 없음"; exit 1; }
D=$(readlink "/proc/$P/cwd" 2>/dev/null)
F="$D/server.js"
NODE=$(readlink "/proc/$P/exe" 2>/dev/null); [ -z "${NODE:-}" ] && NODE=node
echo "대상 파일: $F"
echo "node: $NODE"
[ -f "$F" ] || { echo "결과=server.js 없음 ($F)"; exit 1; }
[ -w "$F" ] || { echo "결과=권한없음 ($F) — 이 사용자로 수정 불가(sudo 필요)"; exit 1; }

INJ=$(curl -fsSL "$INJ_URL")
[ -z "${INJ:-}" ] && { echo "결과=버튼코드 다운로드 실패"; exit 1; }
printf '%s' "$INJ" > /tmp/ysc_inject.html

python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f, encoding='utf-8').read()
if 'ysc-copy' in s or 'ysc-paste' in s:
    print("결과=이미 설치됨 (중복 없음)"); sys.exit(2)
if '</body>' not in s:
    print("결과=</body> 못 찾음 — 중단(원본 안 건드림, 안전)"); sys.exit(1)
inj = open('/tmp/ysc_inject.html', encoding='utf-8').read()
open(f + '.bak', 'w', encoding='utf-8').write(s)          # 백업
open(f, 'w', encoding='utf-8').write(s.replace('</body>', inj + '</body>', 1))
print("삽입 완료 (백업: %s.bak)" % f)
PY
rc=$?
[ "$rc" = 2 ] && exit 0
[ "$rc" != 0 ] && exit "$rc"

# --- 재시작 + 자동 복구 ---
restart() { ( cd "$D" && setsid nohup "$NODE" server.js 18091 >/tmp/ysc_console.log 2>&1 </dev/null & ) ; }
kill "$P" 2>/dev/null; sleep 1; restart; sleep 3

if curl -fsS -o /dev/null "http://127.0.0.1:18091/"; then
    echo "결과=완료! 콘솔 정상 동작 → 브라우저 새로고침하면 버튼 보임"
    echo "되돌리려면: cp \"$F.bak\" \"$F\"  후 콘솔 재시작"
else
    cp "$F.bak" "$F"; sleep 1
    NP=$(pgrep -f "server.js 18091" | head -1); [ -n "${NP:-}" ] && kill "$NP" 2>/dev/null; sleep 1
    restart
    echo "결과=삽입 후 콘솔이 안 떠서 '자동 원상복구'함. 콘솔은 안전(원래대로). 로그: /tmp/ysc_console.log"
fi
