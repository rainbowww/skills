#!/usr/bin/env python3
# 공용 원샷 엔진 — Windows / Linux / macOS 공통. 표준 라이브러리만 사용(의존성 설치 전 실행 가능).
# 진입점: install.bat(🟦 Windows) / install.sh(🟩 Linux·macOS)가 파이썬 확인 후 이 파일을 호출한다.
# 자동화 헌법 준수: 환경조사 → 검사후생성(멱등) → 실제검증 → result.json/log/manifest/SHA256. 무한대기 금지.
# 셀프테스트(검증 후 종료): 환경변수 ONESHOT_SELFTEST=1
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = "rainbowww/skills"
BRANCH = "claude/claude-md-docs-8r1kk7"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/youtube-subtitle-converter"
PORT = 5123
TOTAL = 6
APP_FILES = [
    "app.py", "cli.py", "requirements.txt",
    "backend/__init__.py", "backend/routes.py", "backend/youtube_parser.py",
    "backend/transcriber.py", "backend/formatter.py",
    "frontend/index.html", "frontend/css/style.css", "frontend/js/app.js",
]

DEST = Path.home() / "youtube-subtitle-converter"
WORK = DEST / ".oneshot"
LOG = WORK / "install.log"
IS_WIN = os.name == "nt"
SELFTEST = os.environ.get("ONESHOT_SELFTEST") == "1"

completed: list[str] = []
failed: list[str] = []
skipped: list[str] = []
unknown: list[str] = []
_server: subprocess.Popen | None = None


# ---- 안내(흰)/경고(노랑)/위험(빨강). Windows 콘솔은 색 코드 미지원일 수 있어 접두어 병기 ----
def _c(msg, code):
    if IS_WIN:
        return msg
    return f"\033[{code}m {msg} \033[0m"


def log(line: str) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%F %T} {line}\n")


def info(m): print(_c(m, "47;30m").rstrip()); log(f"INFO  {m}")
def warn(m): print(_c(m, "43;30m").rstrip()); log(f"WARN  {m}")
def danger(m): print(_c(m, "41;97m").rstrip()); log(f"ERROR {m}")


def progress(cur: str, nxt: str, n: int) -> None:
    print(_c(f"CURRENT={cur} | NEXT={nxt} | PROGRESS={n}/{TOTAL}", "46;30m").rstrip())
    log(f"STEP [{n}/{TOTAL}] {cur} -> {nxt}")


def survey() -> dict:
    ip = "n/a"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
    except Exception:
        pass
    port_state = "free"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as t:
            port_state = "IN_USE" if t.connect_ex(("127.0.0.1", PORT)) == 0 else "free"
    except Exception:
        pass
    data = {
        "os": platform.platform(), "python": sys.version.split()[0],
        "arch": platform.machine(), "host": platform.node(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        "ip": ip, "disk_free_mb": shutil.disk_usage(str(Path.home())).free // (1024 * 1024),
        "port_%d" % PORT: port_state,
    }
    log("SURVEY " + json.dumps(data, ensure_ascii=False))
    return data


def fetch(rel: str) -> None:
    out = DEST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    last = None
    for t in range(1, 5):
        try:
            with urllib.request.urlopen(f"{RAW}/{rel}", timeout=60) as r:
                out.write_bytes(r.read())
            return
        except Exception as e:  # noqa: BLE001
            last = e
            warn(f"다운로드 재시도 {t}/4: {rel} (WAIT {t*2}s)")
            time.sleep(t * 2)
    raise RuntimeError(f"필수 파일 다운로드 실패: {rel} ({last})")


def venv_python() -> Path:
    return DEST / (".venv/Scripts/python.exe" if IS_WIN else ".venv/bin/python")


def http_get(path: str, timeout: float = 3.0):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def http_post_status(path: str, body: dict) -> int:
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def write_results(status: str, evidence: str, rollback: str, next_purpose: str) -> None:
    result = {
        "status": status, "evidence_status": evidence,
        "current_destination": "youtube-subtitle-converter", "next_purpose": next_purpose,
        "completed_steps": completed, "failed_steps": failed,
        "skipped_steps": skipped, "unknown_steps": unknown,
        "log_path": str(LOG), "rollback_status": rollback,
        "generated_at": f"{datetime.now():%F %T}",
    }
    (WORK / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest, sums = [], []
    for p in sorted(DEST.rglob("*")):
        if p.is_file() and ".oneshot" not in p.parts and ".venv" not in p.parts:
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            rel = p.relative_to(DEST).as_posix()
            manifest.append({"file": rel, "size": p.stat().st_size, "sha256": h})
            sums.append(f"{h}  {rel}")
    (WORK / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORK / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    info(f"result.json / manifest.json / SHA256SUMS.txt / 로그 → {WORK}")


def rollback(reason: str) -> None:
    warn(f"실패 감지({reason}) — 복구: 띄운 서버 정리 (기존 파일·데이터 보존, 재실행 안전)")
    if _server and _server.poll() is None:
        _server.terminate()
        try:
            _server.wait(timeout=5)
        except Exception:
            _server.kill()


def die(step: str, msg: str) -> None:
    failed.append(step)
    danger(msg)
    rollback(step)
    write_results("FAIL", "PROVEN" if completed else "UNKNOWN", "performed", "복구 후 재실행")
    sys.exit(1)


def main() -> int:
    global _server
    WORK.mkdir(parents=True, exist_ok=True)
    LOG.write_text("", encoding="utf-8")

    # [1] 환경 조사
    progress("환경 조사", "앱 파일 준비", 1)
    survey(); completed.append("survey")

    # [2] 앱 파일 검사 후 다운로드 (멱등: 항상 최신본으로 갱신)
    progress("앱 파일 준비", "가상환경", 2)
    try:
        for f in APP_FILES:
            fetch(f)
    except RuntimeError as e:
        die("download", str(e))
    completed.append("files")

    # [3] 가상환경 (있으면 재사용)
    progress("가상환경", "의존성 설치", 3)
    if venv_python().exists():
        skipped.append("venv_exists"); info("가상환경 이미 있음 — 재사용")
    else:
        r = subprocess.run([sys.executable, "-m", "venv", str(DEST / ".venv")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            log(r.stderr)
            die("venv", "가상환경 생성 실패 (Linux는 python3-venv 설치 필요할 수 있음)")
        completed.append("venv")

    # [4] 의존성 (설치돼 있으면 건너뜀)
    progress("의존성 설치", "서버 기동", 4)
    vpy = str(venv_python())
    check = subprocess.run([vpy, "-c", "import flask, yt_dlp, faster_whisper"], capture_output=True)
    if check.returncode == 0:
        skipped.append("deps_present"); info("필요한 프로그램 이미 설치됨 — 건너뜀")
    else:
        info("필요한 프로그램 설치 중... (처음만, 수 분)")
        subprocess.run([vpy, "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
                       cwd=str(DEST), capture_output=True, text=True)
        r = subprocess.run([vpy, "-m", "pip", "install", "--quiet", "-r", "requirements.txt"],
                           cwd=str(DEST), capture_output=True, text=True)
        if r.returncode != 0:
            log(r.stderr)
            die("deps", f"의존성 설치 실패 (로그: {LOG})")
        completed.append("deps")

    # [5] 서버 기동 + 실제 기능 검증 (timeout, 무한대기 금지)
    progress("서버 기동", "동작 검증", 5)
    _server = subprocess.Popen([vpy, "app.py"], cwd=str(DEST),
                               stdout=(WORK / "server.log").open("w"), stderr=subprocess.STDOUT)
    up = False
    for t in range(1, 31):
        if _server.poll() is not None:
            die("server_died", f"서버가 시작 직후 종료됨 (로그: {WORK/'server.log'})")
        try:
            if http_get("/")[0] == 200:
                up = True; break
        except Exception:
            pass
        print(f"  서버 대기... RETRY={t}/30 WAIT=1s", end="\r"); time.sleep(1)
    print()
    if not up:
        die("server_timeout", "서버가 30초 내에 응답하지 않음")
    try:
        _, home = http_get("/", 5)
        if "자막 변환기" not in home:
            die("verify_home", "메인 페이지 내용 확인 실패")
        code = http_post_status("/api/convert", {"url": "https://naver.com/x"})
        if code != 400:
            die("verify_api", f"API 에러 처리 검증 실패 (기대 400, 실제 {code})")
    except Exception as e:  # noqa: BLE001
        die("verify_exc", f"검증 중 오류: {e}")
    completed.append("verify")

    # [6] 마무리
    progress("마무리", f"http://127.0.0.1:{PORT} 사용", 6)
    write_results("PASS", "PROVEN", "none", f"브라우저에서 http://127.0.0.1:{PORT} 사용")

    if SELFTEST:
        rollback("selftest-cleanup")
        info("SELFTEST 통과 — 검증 후 종료 (status=PASS, evidence=PROVEN)")
        return 0

    info(f"설치·검증 완료 ✅  브라우저에서 http://127.0.0.1:{PORT} 을 여세요. (종료: Ctrl+C)")
    try:
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    except Exception:
        pass
    try:
        _server.wait()
    except KeyboardInterrupt:
        rollback("user-ctrl-c")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        rollback("user-ctrl-c")
        sys.exit(130)
