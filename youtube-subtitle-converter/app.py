#!/usr/bin/env python3
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 또는 윈도우(python 설치 후) — 사람이 직접 실행
"""자막 변환기 웹앱(A 형태) 진입점 — 실행 후 브라우저에서 http://127.0.0.1:5123 접속."""
from backend.routes import create_app

if __name__ == "__main__":
    app = create_app()
    print("자막 변환기 실행 중 → 브라우저에서 http://127.0.0.1:5123 을 여세요 (종료: Ctrl+C)")
    app.run(host="127.0.0.1", port=5123, debug=False)
