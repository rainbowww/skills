# portable-ai-setup — 어디서든 동일한 AI 작업환경

A(회사) / B(자택) / C(학교), OS(Windows/macOS/Linux) 무관하게 **동일한 Fable 5급 AI 행동**을 재현하는 이식형 패키지.

## ⚡ 원샷 설치 (이 한 줄이면 끝 — 최신 버전 자동 다운로드 + 설치 + 파일 열기)

**Windows** — PowerShell 열고 붙여넣기:
```powershell
irm https://raw.githubusercontent.com/rainbowww/skills/main/portable-ai-setup/install.ps1 | iex
```

**macOS / Linux** — 터미널 열고 붙여넣기:
```bash
curl -sSL https://raw.githubusercontent.com/rainbowww/skills/main/portable-ai-setup/install.sh | bash
```

실행하면 `~/portable-ai-setup_Ver{N}` 폴더에 설치되고, 붙여넣을 시스템 프롬프트 파일이 자동으로 열립니다(윈도우). 파일에서 **B절 코드블록 복사 → AI 도구에 붙여넣기** — 그게 전부입니다.

## 빠른 시작 (수동 설치 시, 2분)

| 장소 | 가이드 |
|---|---|
| A 회사 | [`locations/A-company.md`](locations/A-company.md) |
| B 자택 (마스터) | [`locations/B-home.md`](locations/B-home.md) |
| C 학교 (공용 PC) | [`locations/C-school.md`](locations/C-school.md) |

공통 3단계: ① `prompts/universal-system-prompt.md` B절을 AI 도구의 시스템 지침에 붙여넣기 ② Claude Code면 권한을 `acceptEdits`(반자동)로 ③ 프로젝트마다 `templates/CLAUDE.md.template` 복사.

## 내보내기 (오프라인 이동)

- Windows: `.\export.ps1` → `portable-ai-setup_Ver{N}.zip`
- macOS/Linux: `bash export.sh` → `portable-ai-setup_Ver{N}.zip`

## 버전 규칙 (혼동 방지 — 반드시 준수)

같은 이름의 zip이 두 개 돌아다니는 사고를 막기 위한 절대 규칙:

1. **버전의 원천은 `VERSION` 파일 하나뿐.** 현재 버전은 그 파일의 숫자다.
2. **zip 파일명에는 항상 버전이 붙는다** (`portable-ai-setup_Ver2.zip`). export 스크립트가 자동으로 붙이므로 손으로 이름 짓지 말 것.
3. **패키지 내용을 수정하면 배포 전에 `VERSION` 숫자를 +1** 하고 아래 이력표에 한 줄 추가.
4. 버전 없는 zip(`portable-ai-setup.zip`)을 받았다면 **구버전이므로 폐기**하고 최신 Ver본을 받을 것.
5. 세 장소(A/B/C)에서 버전이 다르면, 숫자가 큰 쪽이 항상 최신이다.

### 버전 이력

| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| Ver1 | 2026-07-09 | 최초 패키지 (export.ps1에 윈도우 전용 경로 버그 있음 — 폐기) |
| Ver2 | 2026-07-09 | export.ps1 크로스플랫폼 수정(Join-Path), PowerShell 7.6.3 실테스트 통과, 버전 체계 도입 |
| Ver3 | 2026-07-09 | 원샷 설치기 추가 (install.ps1 / install.sh — 한 줄 실행으로 최신 버전 자동 다운로드·설치) |
| Ver4 | 2026-07-09 | install.ps1 버그 수정: 숫자 VERSION을 Int64로 파싱해 .Trim()에서 죽던 문제([string] 캐스팅) |
| Ver5 | 2026-07-09 | 설치기 재시도 로직 추가: GitHub 429(요청 과다) 시 파일별 최대 4회 재시도 + 요청 간격 0.3초 |
| Ver6 | 2026-07-09 | install.ps1 notepad 자동열기를 Windows 전용으로 가드(맥/리눅스 pwsh는 경로 안내). 13개 파일 전체 다운로드 GitHub 상대 실전 테스트 통과. **실제 Windows PowerShell 5.1에서 사용자 실행 성공 확인** |
| Ver7 | 2026-07-09 | claude.ai "Claude 지침" 필드 붙여넣기 전용본 추가 (`prompts/claudeai-instructions.md` — B절에서 플레이스홀더·중복 안전절·운영자 설명 제거) |
| Ver8 | 2026-07-09 | 복붙 전용 파일 `prompts/PASTE-claude-ai.txt` 추가 — 내용 전체가 붙여넣을 것(Ctrl+A→Ctrl+C, 고를 필요 없음). 설치기가 이 파일을 자동으로 엶 |

## 갱신 규칙

- 수정은 **B 자택에서만** → `git push` → 다른 장소는 `git pull`
- 시스템 프롬프트 재생성: 새 원본 + `prompts/final-work-instruction.md`를 LLM에 투입

## 테스트 상태

| 환경 | export 스크립트 | 상태 |
|---|---|---|
| Linux (샌드박스) | `export.sh` | ✅ 테스트 통과 (2026-07-09) |
| PowerShell 7.6.3 (샌드박스, 실제 실행) | `export.ps1` | ✅ 테스트 통과 (2026-07-09) — 경로를 Join-Path로 교체해 전 OS 호환 |
| macOS | `export.sh` | ⬜ bash 동일 — 현장 확인 시 ✅ 예상 |
| Windows PowerShell 5.1 (실기기) | `install.ps1` 원라이너 | ✅ **실사용 확인** (2026-07-09, 사용자 직접 실행 — Ver6 설치·색상박스·기존설정 보호 전부 정상) |
