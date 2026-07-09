# HERMES 콘솔 버튼 설치

복사/붙여넣기 버튼을 HERMES 콘솔에 추가하는 두 가지 방법

## 방법 1: 직접 설치 (권장)

### 설치 (node40에서 실행)

```bash
bash hermes-console/install_buttons_standalone.sh
```

또는 GitHub에서 다운로드:

```bash
curl -fsSL "https://raw.githubusercontent.com/rainbowww/skills/claude/claude-md-docs-8r1kk7/hermes-console/install_buttons.sh" | bash
```

### 예상 결과

```
PID=12345  node=/usr/bin/node
server.js: /path/to/server.js
삽입 완료 (백업: /path/to/server.js.bak)
결과=완료! 콘솔 정상 → 브라우저 새로고침하면 버튼 보임
```

### 확인

1. HERMES 콘솔 브라우저 새로고침
2. 📋 **복사** 버튼 (응답 상자 우상단)
3. 📋 **붙여넣기(초기화)** 버튼 (입력 textarea 아래)

---

## 방법 2: 프록시 서버 (테스트/데모)

실제 server.js를 수정하지 않고 프록시 서버를 통해 버튼을 테스트할 수 있습니다.

### 실행

```bash
python3 hermes-console/proxy_server.py
```

또는 실제 node40에 연결:

```bash
python3 hermes-console/proxy_server.py --upstream http://192.168.0.40:18091 --port 18092
```

### 접속

http://127.0.0.1:18092/

### 특징

- 📋 **복사** 버튼: 응답 내용을 클립보드로 복사
- 📋 **붙여넣기(초기화)** 버튼: 클립보드 내용으로 입력창 초기화
- 클라이언트 UI만 추가 (안전)
- 원본 server.js 수정 안 함

---

## 파일 설명

| 파일 | 설명 |
|------|------|
| `install_buttons_standalone.sh` | 완전 자립형 설치 스크립트 (권장) |
| `install_buttons.sh` | 원본 설치 스크립트 |
| `inject.html` | 버튼 코드 (클라이언트 UI) |
| `proxy_server.py` | 프록시 서버 (테스트용) |
| `server.js.example_with_buttons_installed` | 설치 완료 후 상태 참조 파일 |
| `DEPLOYMENT_LOG.md` | 배포 로그 (예상 출력) |

---

## 안전성

✓ **백업**: 설치 전 자동 백업 (server.js.bak)
✓ **복구**: 재시작 실패 시 자동 복구
✓ **검증**: 중복 설치 방지
✓ **클라이언트 UI**: 서버 명령 실행 없음

---

## 트러블슈팅

### "콘솔서버(server.js 18091) 없음"
→ node40에서 실행하세요

### "권한없음"
→ `sudo bash hermes-console/install_buttons_standalone.sh`

### 설치 후 버튼이 안 보임
1. 브라우저 캐시 삭제
2. Ctrl+Shift+Delete 눌러 캐시 비우기
3. 새로고침 (F5)

### 버튼을 되돌리고 싶음
```bash
cp /path/to/server.js.bak /path/to/server.js
# node 재시작
```
