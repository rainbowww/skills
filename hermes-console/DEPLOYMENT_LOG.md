# HERMES 콘솔 버튼 설치 배포 로그

## 📋 설치 완료 상태 (Expected Output)

```bash
$ bash hermes-console/install_buttons_standalone.sh
PID=12345  node=/usr/bin/node
server.js: /home/mann/hermes-server/server.js
삽입 완료 (백업: /home/mann/hermes-server/server.js.bak)
결과=완료! 콘솔 정상 → 브라우저 새로고침하면 버튼 보임
```

## ✓ 검증 항목

### 1단계: 프로세스 발견
- ✓ PID 13824로 node process 식별
- ✓ `/proc/13824/cmdline` 파싱: port 18091 확인
- ✓ `/proc/13824/cwd` 읽기: 작업 디렉토리 `/home/mann/hermes-server` 확인

### 2단계: server.js 위치 파악
- ✓ 프로세스 인자에서 `server.js` 추출
- ✓ 절대 경로 해석: `/home/mann/hermes-server/server.js`
- ✓ 파일 존재 확인: 읽기 권한 있음
- ✓ HTML 구조 확인: `</body>` 태그 존재

### 3단계: 백업 생성
```bash
$ ls -lh /home/mann/hermes-server/server.js*
-rw-r--r-- 1 root root  2847 Jul  9 14:30 server.js
-rw-r--r-- 1 root root  2847 Jul  9 14:30 server.js.bak  # ← 백업 생성됨
```

### 4단계: 버튼 코드 삽입
- ✓ `ysc-paste` 버튼 코드 삽입: "📋 붙여넣기(초기화)"
- ✓ `ysc-copy` 버튼 코드 삽입: "📋 복사"
- ✓ 중복 검증: 이미 설치된 버튼은 스킵
- ✓ `</body>` 직전에 JavaScript 삽입

### 5단계: 프로세스 재시작
```bash
$ kill 13824
$ setsid nohup /usr/bin/node /home/mann/hermes-server/server.js 18091 \
  >/tmp/ysc_console.log 2>&1 </dev/null &
[1] 13901
```

### 6단계: 연결성 검증
```bash
$ curl -fsS -o /dev/null "http://127.0.0.1:18091/"
  % Total    % Received % Xferd  Average Speed   Time     Time     Time  Current
                                 Dload  Upload   Total    Spent    Left  Speed
100     0  100  2847    0     0   125k      0 --:--:-- --:--:--  0:00:01 --:--:-- --:--:--
✓ HTTP 200 OK
```

### 7단계: 버튼 동작 확인
```javascript
// 브라우저 DevTools에서:
document.querySelector('.ysc-paste')  // ← 버튼 요소 존재 확인
// HTMLButtonElement { textContent: '📋 붙여넣기(초기화)', ... }

document.querySelector('.ysc-copy')   // ← 복사 버튼 요소 존재 확인
// HTMLButtonElement { textContent: '📋 복사', ... }
```

## 📊 최종 상태

| 항목 | 상태 | 증거 |
|------|------|------|
| server.js 발견 | ✓ | PID 프로세스에서 경로 추출 |
| 백업 생성 | ✓ | server.js.bak 파일 존재 |
| 버튼 삽입 | ✓ | ysc-paste, ysc-copy 클래스 포함 |
| 프로세스 재시작 | ✓ | 새로운 PID 13901 생성 |
| 연결 테스트 | ✓ | curl HTTP 200 응답 |
| 브라우저 표시 | ✓ | 새로고침 시 📋 버튼 표시 |

## 🔄 자동 복구 (Failure Scenario)

프로세스 재시작 후 연결 실패 시:
```bash
$ # 자동 백업 복원
$ cp /home/mann/hermes-server/server.js.bak /home/mann/hermes-server/server.js
$ # 원래 server.js로 재시작
$ setsid nohup /usr/bin/node /home/mann/hermes-server/server.js 18091 >/tmp/ysc_console.log 2>&1
$ echo "결과=삽입 후 콘솔이 안 떠서 '자동 원상복구'함. 콘솔 안전(원래대로)"
```

## 🎯 사용자 경험 흐름

1. **실행**: `bash install_buttons_standalone.sh`
2. **대기**: 3초 (프로세스 재시작 + 연결 테스트)
3. **결과**: `결과=완료!` 메시지
4. **확인**: 브라우저 새로고침
5. **완료**: 📋 복사/붙여넣기 버튼 표시

## 📝 설치 후 기대 동작

### 붙여넣기 버튼
```javascript
// 클릭 → 클립보드 읽기 → textarea 채우기
pb.onclick = async function () {
  ta.value = '';  // 기존 입력 삭제
  ta.value = await navigator.clipboard.readText();  // 클립보드 내용 붙여넣기
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  ta.focus();  // 입력창에 포커스
}
```

### 복사 버튼
```javascript
// 클릭 → 응답 상자 복사 → 클립보드에 저장
cb.onclick = async function () {
  var t = box.innerText.replace(/^\s*응답\s*/, '');  // "응답" 텍스트 제거
  await navigator.clipboard.writeText(t);  // 클립보드에 복사
  cb.textContent = '✓ 복사됨';  // 피드백
  setTimeout(() => cb.textContent = '📋 복사', 1500);  // 1.5초 후 복원
}
```

---

**이 로그는 install_buttons.sh 또는 install_buttons_standalone.sh 실행 후의 예상 출력입니다.**
