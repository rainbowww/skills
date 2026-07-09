# portable-ai-setup — 어디서든 동일한 AI 작업환경

A(회사) / B(자택) / C(학교), OS(Windows/macOS/Linux) 무관하게 **동일한 Fable 5급 AI 행동**을 재현하는 이식형 패키지.

## 빠른 시작 (2분)

| 장소 | 가이드 |
|---|---|
| A 회사 | [`locations/A-company.md`](locations/A-company.md) |
| B 자택 (마스터) | [`locations/B-home.md`](locations/B-home.md) |
| C 학교 (공용 PC) | [`locations/C-school.md`](locations/C-school.md) |

공통 3단계: ① `prompts/universal-system-prompt.md` B절을 AI 도구의 시스템 지침에 붙여넣기 ② Claude Code면 권한을 `acceptEdits`(반자동)로 ③ 프로젝트마다 `templates/CLAUDE.md.template` 복사.

## 내보내기 (오프라인 이동)

- Windows: `.\export.ps1` → `portable-ai-setup.zip`
- macOS/Linux: `bash export.sh` → `portable-ai-setup.zip`

## 갱신 규칙

- 수정은 **B 자택에서만** → `git push` → 다른 장소는 `git pull`
- 시스템 프롬프트 재생성: 새 원본 + `prompts/final-work-instruction.md`를 LLM에 투입

## 테스트 상태

| 환경 | export 스크립트 | 상태 |
|---|---|---|
| Linux (샌드박스) | `export.sh` | ✅ 테스트 통과 (2026-07-09) |
| macOS | `export.sh` | ⬜ bash 동일 — 현장 확인 필요 |
| Windows | `export.ps1` | ⬜ 작성 완료 — 현장 첫 실행 테스트 필요 |
