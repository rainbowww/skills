# 원샷 자동화 프로젝트 헌법

이 프로젝트의 설치·실행 스크립트는 아래 헌법을 따른다. (사용자 제공, 2026-07-09)

- 무인/무개입/원샷: 실행 후 추가 입력 없이 최종 결과까지 진행. OS별 대표 진입점 1개(Windows=BAT→PowerShell, Linux=SH).
- 최소 변경 / 검사 후 생성 / 재실행 안전(멱등).
- 환경 자동 조사 → 로그 기록 후 변경 시작.
- 실제 기능 검증(파일 존재만으로 성공 선언 금지): 포트·HTTP 응답·API 동작 확인.
- 상태 판정: PASS/PARTIAL/FAIL + 증거 PROVEN/INFERRED/PROPOSED_NOT_EXECUTED/UNKNOWN.
- 산출물: 전체 로그 + result.json + manifest.json + SHA256SUMS.txt.
- 진행률 표시(CURRENT DESTINATION/NEXT PURPOSE/PROGRESS/RETRY/WAIT), timeout 필수, 무한대기 금지.
- 실패 시 백업·롤백, 비밀값 로그 평문 금지, 다운로드 출처·해시 확인.
- 코드 일부 교체·수동 이동을 사용자에게 요구하지 않음. 실행 안 한 코드를 성공이라 표기하지 않음.

전문은 프로젝트 지시(2026-07-09 업로드)에 따른다.
