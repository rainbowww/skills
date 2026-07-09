# 인수인계 작업계획서 — HERMES 콘솔 복사/붙여넣기 버튼

> 다음 담당(사령관/LLM)이 그대로 이어받도록 작성. 추측과 검증사실을 분리해 표기한다.
> **[PROVEN]** = 이 환경에서 실제 실행해 확인함. **[INFERRED]** = 정황상 추정(미검증).

---

## 0. 한 줄 요약

node40(192.168.0.40:18091)의 HERMES 콘솔 `server.js` HTML에 버튼 2개
(📋 복사 / 📋 붙여넣기(초기화))를 주입하는 작업. **핵심 명령은 아래 §5의
"한 번 붙여넣기"이며, 이 저장소 안에서 실제로 동작을 증명했다.**

## 1. 목표(설계)

HERMES 콘솔 웹 UI에 클라이언트 측 버튼 2개를 추가한다. 서버 명령 실행 로직은
건드리지 않는다(순수 UI 주입).

| 버튼 | class | 위치 | 동작 |
|------|-------|------|------|
| 📋 붙여넣기(초기화) | `ysc-paste` | 입력 textarea 옆 | textarea 비우고 `navigator.clipboard.readText()`로 채움 |
| 📋 복사 | `ysc-copy` | "응답" 상자 우상단 | 응답 본문을 `navigator.clipboard.writeText()`로 복사 |

주입 방식: `server.js`가 문자열로 들고 있는 HTML의 `</body>` 직전에 `<script>`
블록(자가복원 `setInterval(add,1500)` 포함)을 1회 삽입. 버튼 코드 원문은
`hermes-console/install_buttons_oneshot.py`의 `BTN` 상수에 있다.

## 2. 대상 시스템의 확인된 사실 (node40 실제 출력에서)

- **[PROVEN — node40 출력]** `server.js` 실경로: **`/home/mann/fleet-status-board/server.js`**
  (초기 추정 `/home/mann/hermes-server/...`는 **오답**이었다. 실경로로 확정.)
- **[PROVEN — node40 출력]** 기동: `node=/usr/bin/node`, 최근 PID 예: `662758`, 포트 `18091`.
- **[PROVEN — node40 출력]** 어느 시점의 실행에서 `결과=이미 설치됨(중복 없음)`이
  나온 바 있음 → **버튼이 이미 들어가 있을 가능성이 높다.** 다음 담당은 설치 전
  §6 "현재 상태 점검"부터 하라(중복 작업 방지).

## 3. 왜 지금까지 "실패"였나 (근본원인)

- 실패 로그: `bash: hermes-console/install_buttons_standalone.sh: No such file or directory` (rc=127),
  `python3: can't open file '.../proxy_server.py'` (rc=2).
- **근본원인은 네트워크 격리가 아니다.** node40는 명령을 실행하고 stdout/stderr를
  되돌려줬다 → **명령 통로는 살아있다.** 진짜 원인은 보낸 명령이 *저장소 체크아웃에
  있는 파일*(`hermes-console/install_buttons_standalone.sh`)에 의존했는데, node40의
  실행 위치엔 그 파일이 없었던 것(경로/미(未)pull 문제).
- **교훈 → 해결책:** 파일 의존을 제거한 **self-contained "한 번 붙여넣기"** 로 전환.
  아래 §5가 그것이며, 파일이 없어도 stdin으로 통째 실행된다.

## 4. 산출물 (이 저장소, 브랜치 `claude/claude-md-docs-8r1kk7`)

| 파일 | 역할 | 상태 |
|------|------|------|
| `hermes-console/install_buttons_oneshot.py` | **[권장]** 자립형 설치기. 파일 미존재에도 stdin 실행 가능 | **[PROVEN] 로컬 E2E 통과** |
| `hermes-console/run_hermes_with_buttons.py` | 버튼 내장 콘솔(테스트/데모용 독립 서버) | 동작 확인 |
| `hermes-console/proxy_server.py` | server.js 미수정 프록시 주입(테스트) | 동작 확인 |
| `hermes-console/install_buttons_standalone.sh` | 구(舊) bash 설치기 | 참고용(경로의존 이슈로 비권장) |
| `hermes-console/inject.html` | 버튼 코드 원문 | 참고 |

## 5. 앞으로의 계획 — 다음 담당이 실행할 "한 번 붙여넣기"

node40 셸(또는 HERMES 콘솔의 명령 실행창)에 **아래 블록을 통째로 한 번** 붙여넣는다.
파일이 없어도 동작한다(이번 실패의 재발 방지). `PYEOF`까지 포함해 붙여넣을 것.

```bash
# 🟩 node40 (Linux bash) — 아래 전체를 한 번에 붙여넣기
python3 - <<'PYEOF'
# hermes-console/install_buttons_oneshot.py 의 전체 내용을 여기에 붙여넣는다.
# (저장소 파일을 열어 그대로 복사. 길이 때문에 본 문서엔 경로만 표기.)
PYEOF
```

- 저장소에서 pull이 가능하면 더 간단:
  ```bash
  # 🟩 node40 (Linux bash)
  cd /home/mann/fleet-status-board 2>/dev/null; \
  python3 "$(git -C /path/to/skills rev-parse --show-toplevel)/hermes-console/install_buttons_oneshot.py"
  ```
  단, **경로 의존이 다시 문제될 수 있으니** 원칙은 위의 stdin(`<<'PYEOF'`) 방식.

### 설치기 동작(요약)
1. `/proc/net/tcp(6)` + `/proc/*/fd`로 18091 LISTEN PID 자동 탐지(ss/lsof 불요).
2. PID의 cmdline/cwd에서 `server.js` 실경로 추출. 실패 시 알려진 경로
   `/home/mann/fleet-status-board/server.js` → 재귀 탐색 순으로 폴백.
3. 이미 `ysc-paste` 있으면 `이미 설치됨(중복 없음)` 출력 후 종료(멱등).
4. `server.js.bak` 백업 → `</body>` 직전 버튼 주입.
5. 프로세스 재시작(`setsid nohup node server.js 18091`) → HTTP 200 검증.
6. 검증 실패 시 백업 자동 복구(원상복귀) 후 그 사실을 출력.

## 6. 현재 상태 점검 & 설치 후 검증 (다음 담당 필수)

```bash
# 🟩 node40 (Linux bash) — 설치 전/후 공통 점검
# (1) 버튼이 이미 있는지
grep -c ysc-paste /home/mann/fleet-status-board/server.js
# (2) 콘솔이 실제로 버튼을 서빙하는지 (0보다 크면 성공)
curl -fsS http://127.0.0.1:18091/ | grep -c 'ysc-paste'
```
브라우저에서 최종 확인: 콘솔 새로고침 → 입력창 옆 "📋 붙여넣기(초기화)",
응답 상자 우상단 "📋 복사"가 보이면 완료.
(클립보드 API는 https 또는 localhost 접속에서만 동작 — 접속 URL 확인.)

## 7. 롤백

```bash
# 🟩 node40 (Linux bash)
cp /home/mann/fleet-status-board/server.js.bak /home/mann/fleet-status-board/server.js
# 이후 node 프로세스 재시작(설치기와 동일 방식) 하면 원상복귀
```

## 8. 로컬 검증 기록 (이 저장소 환경에서, node40 아님)

- **[PROVEN]** 목(mock) node 서버를 18091에 `setsid nohup`으로 띄우고 설치기 실행:
  PID 자동탐지 → 백업 생성 → 주입 → 재시작 → `curl`로 HTTP 200 및 응답 본문에서
  `ysc-paste/ysc-copy/📋 복사/📋 붙여넣기(초기화)` 4종 확인.
- **[PROVEN]** 재실행 시 `이미 설치됨(중복 없음)`, 백업엔 버튼 0개(원본 보존).
- **[INFERRED]** node40 실환경도 동일 커널 인터페이스(/proc, setsid, curl 불필요)를
  쓰므로 동일하게 동작할 것으로 판단. 단 node40에서의 최종 실행·확인은 미수행
  (이 환경은 사설망 192.168.0.40에 직접 도달 불가). 통로가 있는 담당이 §5를 실행해
  마무리해야 함.
