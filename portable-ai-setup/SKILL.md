---
name: portable-ai-setup
description: Portable universal AI assistant setup for use across multiple locations (company/home/school). Reproduces Claude Fable 5-quality behavior on Claude Opus 4.8 and other models via a universal system prompt, a reusable CLAUDE.md template, and per-location install profiles. Keywords - system prompt, universal, portable, CLAUDE.md, Fable 5, Opus 4.8, 반자동, 시스템프롬프트, 범용, 이식
---

# Portable AI Setup (범용 AI 작업환경 이식 스킬)

어느 장소(A 회사 / B 자택 / C 학교)에서든 **동일한 고품질 AI 어시스턴트 행동**을 재현하기 위한 이식형 패키지.

## When to use

**Activate this skill when the user requests:**
- 새 장소/새 컴퓨터에서 AI 작업환경을 동일하게 세팅
- 범용 시스템 프롬프트 적용 또는 갱신
- CLAUDE.md 초기 설정
- Fable 5 수준 행동을 Opus 4.8 등 다른 모델에서 재현

**Do NOT activate for:** 일반 코딩 질문, 이 패키지와 무관한 프롬프트 작성.

## Package contents

| 파일 | 용도 |
|---|---|
| `prompts/universal-system-prompt.md` | 범용 고성능 시스템 프롬프트 (개인화 완성본, A~D 구조) |
| `prompts/final-work-instruction.md` | 시스템 프롬프트를 재생성/갱신할 때 쓰는 "최종 작업 지시 프롬프트" 원본 |
| `templates/CLAUDE.md.template` | 어느 프로젝트에나 재사용 가능한 CLAUDE.md 템플릿 |
| `locations/A-company.md` | A 회사 설치 프로필 |
| `locations/B-home.md` | B 자택 설치 프로필 |
| `locations/C-school.md` | C 학교 설치 프로필 |
| `export.sh` | 스킬 내보내기 (zip 생성) |

## Install (any location)

```bash
git clone https://github.com/rainbowww/skills   # 또는 zip 다운로드
cd skills/portable-ai-setup
bash export.sh        # portable-ai-setup.zip 생성 (USB/메일 이동용)
```

그 다음 해당 장소의 `locations/*.md` 프로필을 따르세요. 핵심은 3단계뿐:

1. **시스템 프롬프트**: `prompts/universal-system-prompt.md`의 B절 완성본을 사용하는 도구(Claude.ai 프로젝트 지침, Claude Code CLAUDE.md, 타 모델 system 영역)에 붙여넣기
2. **프로젝트 규칙**: 새 프로젝트마다 `templates/CLAUDE.md.template` 복사 → 대괄호만 채움
3. **권한(Claude Code)**: `~/.claude/settings.json`에 `{"permissions": {"defaultMode": "acceptEdits"}}` (반자동)

## Design principles (why this works everywhere)

- **모델 독립**: 고유명·날짜·도구 스키마는 전부 플레이스홀더. Fable 5 행동은 Anthropic 공식 마이그레이션 가이드의 검증된 프롬프트 스니펫으로 재현.
- **git = 내보내기**: 저장소 자체가 이동 수단. 장소별 차이는 `locations/`에만 격리.
- **반자동(semi-auto)**: 루틴 작업은 자동 진행, 되돌리기 어려운 것만 확인 — 사용자의 확정 운영 방식.
