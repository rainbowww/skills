# C — 학교 설치 프로필

> 전제: 공용 PC일 수 있음. **개인 정보를 기기에 남기지 않는 것**이 최우선.

## 설치 (OS별)

**Windows (PowerShell):**
```powershell
# 공용 PC라면 clone 대신 USB의 zip 사용 권장
Expand-Archive portable-ai-setup.zip -DestinationPath $env:TEMP\pai

# ⚠️ 공용 PC는 .ps1 실행이 기본 차단(ExecutionPolicy Restricted)됨.
# 관리자 권한 없이 이번 세션만 우회하려면:
powershell -ExecutionPolicy Bypass -File .\export.ps1
```

**macOS / Linux (bash):**
```bash
unzip portable-ai-setup.zip -d /tmp/pai
```

## 적용

1. `prompts/universal-system-prompt.md` B절을 **복사해서** AI 도구에 붙여넣기 (파일을 기기에 영구 저장하지 않기)
2. 공용 PC에서는 `~/.claude/settings.json` 수정 대신 세션 내 설정 사용 (Claude Code면 `Shift+Tab`으로 acceptEdits 전환)
3. 개인 프로젝트 작업은 지양, 브라우저 기반 도구(claude.ai) 위주 사용

## 공용 PC 필수 수칙

- **로그아웃 확인**: AI 서비스·GitHub 전부, 사용 끝나면 로그아웃 + 브라우저 시크릿 모드 권장
- 임시 폴더(`$env:TEMP` / `/tmp`)에 푼 파일은 사용 후 삭제
- API 키·토큰을 공용 PC에 절대 입력·저장하지 않기
- git 자격증명 저장(credential helper) 사용 금지
