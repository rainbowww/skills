#!/usr/bin/env python3
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 또는 윈도우(python 설치 후) — 사람이 직접 실행
"""자막 변환기 웹앱(A 형태) 진입점.

기본: PC 전용(http://127.0.0.1:5123) — 안전.
폰 접속(같은 와이파이): 환경변수 YSC_HOST=0.0.0.0 로 실행하면
  서버가 LAN에 열리고, 폰에서 열 주소(http://<PC-IP>:5123)를 화면에 찍어줍니다.
"""
import os
import socket

from backend.routes import create_app

PORT = 5123


def _lan_ip() -> str:
    """이 PC의 사설 IP(예: 192.168.x.x)를 알아낸다. 실패 시 빈 문자열."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 실제로 보내지 않음 — 라우팅 확인용
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ""


if __name__ == "__main__":
    host = os.environ.get("YSC_HOST", "127.0.0.1")
    app = create_app()
    if host == "0.0.0.0":
        ip = _lan_ip() or "<이-PC의-IP>"
        print("=" * 56)
        print("자막 변환기 실행 중 (폰 접속 허용 모드)")
        print(f"  이 PC에서   : http://127.0.0.1:{PORT}")
        print(f"  폰/다른기기 : http://{ip}:{PORT}   (같은 와이파이)")
        print("  ※ 처음 실행 시 방화벽 허용 창이 뜨면 '허용'을 누르세요.")
        print("=" * 56)
    else:
        print(f"자막 변환기 실행 중 → 브라우저에서 http://127.0.0.1:{PORT} 을 여세요 (종료: Ctrl+C)")
        print("  (폰에서도 보려면: 폰접속 모드로 다시 실행 — 아래 안내 참고)")
    app.run(host=host, port=PORT, debug=False)
