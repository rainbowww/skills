# B — 자택 설치 프로필

> 전제: 본인 소유 PC, 제약 최소. 여기가 마스터(원본 갱신 장소).

## 설치 (OS별)

**Windows (PowerShell):**
```powershell
git clone https://github.com/rainbowww/skills
cd skills\portable-ai-setup
.\export.ps1    # 회사/학교 반입용 zip 생성
```

**macOS / Linux (bash):**
```bash
git clone https://github.com/rainbowww/skills
cd skills/portable-ai-setup
bash export.sh   # 회사/학교 반입용 zip 생성
```

## 적용 3단계 (A 프로필과 동일)

1. `prompts/universal-system-prompt.md` B절 → AI 도구 시스템 지침에
2. `~/.claude/settings.json` (Windows: `%USERPROFILE%\.claude\settings.json`) → `{ "permissions": { "defaultMode": "acceptEdits" } }`
3. 프로젝트마다 `templates/CLAUDE.md.template` → `CLAUDE.md`

## 자택 = 마스터 역할

- 프롬프트 개선은 **여기서만** 하고 git push → 회사/학교는 `git pull`만. (세 곳에서 제각각 고치면 버전이 갈라짐)
- 시스템 프롬프트를 갱신하고 싶으면: 새 원본 + `prompts/final-work-instruction.md` 전문을 LLM에 투입 → 결과로 `universal-system-prompt.md` 교체 → 커밋·푸시
