# A — 회사 설치 프로필

> 전제: 회사 PC는 관리자 권한·외부 사이트 접근이 제한될 수 있음. 보안 정책 우선.

## 설치 (OS별)

**Windows (PowerShell):**
```powershell
git clone https://github.com/rainbowww/skills
# git 차단 시: GitHub 웹 → Code → Download ZIP, 또는 USB의 portable-ai-setup.zip 사용
```

**macOS / Linux (bash):**
```bash
git clone https://github.com/rainbowww/skills
```

## 적용 3단계

1. **시스템 프롬프트**: `prompts/universal-system-prompt.md` B절 → 사용하는 AI 도구의 시스템/프로젝트 지침 영역에 붙여넣기
2. **Claude Code 권한 (반자동)**:
   - Windows: `notepad $env:USERPROFILE\.claude\settings.json`
   - macOS/Linux: `nano ~/.claude/settings.json`
   - 내용: `{ "permissions": { "defaultMode": "acceptEdits" } }`
3. **프로젝트 규칙**: 프로젝트 루트에 `templates/CLAUDE.md.template` 복사 → `CLAUDE.md`로 이름 변경 → 대괄호 채우기

## 회사 전용 주의사항

- **회사 기밀·소스코드를 외부 AI에 넣기 전에 사내 정책 확인** — 이 패키지의 프롬프트 자체에는 개인정보·기밀이 없어 안전하게 반입 가능
- 개인 계정(GitHub 등) 로그인 정보를 회사 PC 브라우저에 저장하지 말 것
- 회사 프록시로 git이 막히면 ZIP 다운로드 방식 사용
