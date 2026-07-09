#!/usr/bin/env bash
# HERMES 콘솔(18091을 서빙하는 node ...server.js)의 HTML에 복사/붙여넣기 버튼을 넣는다.
# 안전: ① 백업 먼저 ② 삽입 후 콘솔이 안 뜨면 '자동 원상복구'. 콘솔을 죽은 채 두지 않는다.
# server.js 경로는 '프로세스의 실제 실행 인자'에서 정확히 읽는다(cwd 가정 안 함).
set -u

INJ_URL="https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/hermes-console/inject.html"

# 1) 18091을 서빙하는 node 프로세스 찾기
P=""
for pid in $(pgrep -f "server.js" 2>/dev/null); do
  if tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q "18091"; then P=$pid; break; fi
done
[ -z "${P:-}" ] && { echo "결과=이 노드에 콘솔서버(server.js 18091) 없음 → 다른 노드에서 실행하세요"; exit 1; }

# 2) server.js 실제 경로 (cmdline 인자 + cwd 로 해석; 절대경로면 그대로)
D=$(readlink "/proc/$P/cwd" 2>/dev/null)
NODE=$(readlink "/proc/$P/exe" 2>/dev/null); [ -z "${NODE:-}" ] && NODE=node
JSARG=$(tr '\0' '\n' < "/proc/$P/cmdline" 2>/dev/null | grep -E '\.js$' | head -1)
case "$JSARG" in
  /*) F="$JSARG" ;;
  "") F="" ;;
  *)  F="$D/$JSARG" ;;
esac
# 그래도 못 찾으면: cwd·흔한 경로에서 '18091'과 '</body>'가 든 server.js 검색(폴백)
if [ -z "${F:-}" ] || [ ! -f "$F" ]; then
  F=$(grep -rlsF "18091" "$D" /opt /srv /home /usr/local 2>/dev/null | grep -E 'server\.js$' | while read -r x; do grep -qF "</body>" "$x" && echo "$x" && break; done | head -1)
fi
echo "PID=$P  node=$NODE"
echo "server.js: ${F:-(못 찾음)}"
[ -n "${F:-}" ] && [ -f "$F" ] || { echo "결과=server.js 실제 파일을 못 찾음 (PID=$P, cwd=$D, arg=$JSARG)"; exit 1; }
[ -w "$F" ] || { echo "결과=권한없음 ($F) — sudo 필요"; exit 1; }
grep -qF "</body>" "$F" || { echo "결과=이 server.js에 </body> 없음(HTML 서빙 방식 다름) — 중단(안전)"; exit 1; }

# 3) 버튼 코드 받기
INJ=$(curl -fsSL "$INJ_URL")
[ -z "${INJ:-}" ] && { echo "결과=버튼코드 다운로드 실패"; exit 1; }
printf '%s' "$INJ" > /tmp/ysc_inject.html

# 4) 백업 + 삽입
python3 - "$F" <<'PY'
import sys
f = sys.argv[1]
s = open(f, encoding='utf-8').read()
if 'ysc-copy' in s or 'ysc-paste' in s:
    print("결과=이미 설치됨(중복 없음)"); sys.exit(2)
if '</body>' not in s:
    print("결과=</body> 없음 — 중단(안전)"); sys.exit(1)
inj = open('/tmp/ysc_inject.html', encoding='utf-8').read()
open(f + '.bak', 'w', encoding='utf-8').write(s)
open(f, 'w', encoding='utf-8').write(s.replace('</body>', inj + '</body>', 1))
print("삽입 완료 (백업: %s.bak)" % f)
PY
rc=$?
[ "$rc" = "2" ] && exit 0
[ "$rc" != "0" ] && exit "$rc"

# 5) 재시작 + 자동 복구
restart() { ( cd "$D" && setsid nohup "$NODE" "$F" 18091 >/tmp/ysc_console.log 2>&1 </dev/null & ) ; }
kill "$P" 2>/dev/null; sleep 1; restart; sleep 3
if curl -fsS -o /dev/null "http://127.0.0.1:18091/"; then
    echo "결과=완료! 콘솔 정상 → 브라우저 새로고침하면 버튼 보임 (되돌리기: cp \"$F.bak\" \"$F\")"
else
    cp "$F.bak" "$F"; sleep 1
    NP=$(pgrep -f "server.js" 2>/dev/null | while read -r q; do tr '\0' ' ' < /proc/$q/cmdline 2>/dev/null | grep -q 18091 && echo "$q" && break; done | head -1)
    [ -n "${NP:-}" ] && kill "$NP" 2>/dev/null; sleep 1; restart
    echo "결과=삽입 후 콘솔이 안 떠서 '자동 원상복구'함. 콘솔 안전(원래대로). 로그: /tmp/ysc_console.log"
fi
