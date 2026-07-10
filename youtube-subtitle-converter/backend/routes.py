"""Flask API 라우트 — 웹 UI(A 형태)가 호출하는 백엔드.

친철 원칙: 변환은 몇 분 걸릴 수 있으므로 '작업(job)'으로 백그라운드 실행하고,
프런트가 /api/progress 를 폴링해 **단계·실제 진행률(%)·상세(파일크기/경과)**를
실시간으로 보여준다. "진짜 받고 있는지, 뭘 받았는지"를 사용자가 항상 알 수 있게.
"""
from __future__ import annotations

import tempfile
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# job_id -> 진행상태 dict. 락으로 보호(백그라운드 스레드가 갱신, 폴링이 읽음).
_jobs: dict[str, dict] = {}
_lock = threading.Lock()
_JOB_TTL = 3600  # 끝난 작업은 1시간 뒤 정리


def _mmss(sec: float) -> str:
    sec = int(sec or 0)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _set(job_id: str, **kw) -> None:
    with _lock:
        j = _jobs.get(job_id)
        if j is not None:
            j.update(kw)


def _purge_old() -> None:
    now = time.time()
    with _lock:
        for jid in [k for k, v in _jobs.items()
                    if v.get("done") and now - v.get("ended", now) > _JOB_TTL]:
            _jobs.pop(jid, None)


def _worker(job_id: str, url: str, include_ts: bool, model_size: str) -> None:
    from .youtube_parser import download_audio
    from .transcriber import transcribe_audio
    from .formatter import format_subtitles
    from .captions import fetch_captions

    try:
        # [1순위] 영상에 이미 있는 자막(VTT)을 먼저 가져온다 — 빠르고 안정적, STT 불필요.
        _set(job_id, stage="자막 확인", percent=5, detail="영상에 있는 자막을 먼저 찾는 중...")
        cap = None
        try:
            cap = fetch_captions(url)
        except Exception:  # noqa: BLE001 — 실패는 조용히 폴백
            cap = None

        if cap:
            segments, title = cap
            _set(job_id, title=title, stage="자막 가져옴", percent=96,
                 detail=f"영상에 있던 자막을 바로 가져왔어요 · 문장 {len(segments)}개")
        else:
            # [폴백] 자막이 없으면 우리 엔진(Whisper)이 목소리로 직접 만든다.
            # 자막 없다고 장애 학생을 빈손으로 돌려보내지 않는다.
            _set(job_id, stage="자막 없음 → 직접 생성", percent=8,
                 detail="영상에 자막이 없어, 목소리로 직접 만들어요 (조금 걸려요)")
            with tempfile.TemporaryDirectory(prefix="subconv_") as tmp:

                def dl_cb(d: dict) -> None:
                    total = d.get("total") or 0
                    got = d.get("downloaded") or 0
                    if d.get("status") == "downloading":
                        pct = 10 + (got / total * 35 if total else 0)
                        mb = got / 1_000_000
                        parts = [f"오디오 내려받는 중  {mb:.1f}MB"]
                        if total:
                            parts[0] += f" / {total/1_000_000:.1f}MB"
                        if d.get("speed"):
                            parts.append(f"{d['speed']/1_000_000:.1f}MB/s")
                        if d.get("eta"):
                            parts.append(f"남은 시간 약 {_mmss(d['eta'])}")
                        _set(job_id, stage="다운로드", percent=int(min(45, pct)),
                             detail="  ·  ".join(parts))
                    elif d.get("status") == "finished":
                        _set(job_id, stage="다운로드", percent=45,
                             detail="오디오 받기 완료 — 음성 인식을 준비합니다")

                audio_path, title = download_audio(url, tmp, progress_cb=dl_cb)
                _set(job_id, title=title)

                def model_cb() -> None:
                    _set(job_id, stage="음성 인식 준비", percent=47,
                         detail="음성 인식 모델을 준비하고 있어요 (처음 한 번은 수 분 걸릴 수 있어요)")

                def tr_cb(cur: float, total: float, n: int) -> None:
                    pct = 50 + (cur / total * 47 if total else 0)
                    detail = f"음성을 글로 옮기는 중  {_mmss(cur)}"
                    if total:
                        detail += f" / {_mmss(total)}"
                    detail += f"  ·  문장 {n}개 인식"
                    _set(job_id, stage="음성 인식", percent=int(min(97, pct)), detail=detail)

                segments = transcribe_audio(
                    audio_path, model_size=model_size, progress_cb=tr_cb, model_cb=model_cb
                )

        _set(job_id, stage="정리", percent=98, detail="자막을 보기 좋게 정리하고 있어요")
        text = format_subtitles(segments, include_timestamp=include_ts)
        with _lock:
            j = _jobs.get(job_id)
            if j is not None:
                j.update(stage="완료", percent=100, done=True, ended=time.time(),
                         detail=f"완료! 문장 {len(segments)}개를 자막으로 만들었어요",
                         result={"title": j.get("title", "자막"), "text": text,
                                 "sentences": len(segments)})
    except (ValueError, RuntimeError) as e:
        _set(job_id, stage="오류", done=True, ended=time.time(), error=str(e))
    except Exception as e:  # noqa: BLE001
        _set(job_id, stage="오류", done=True, ended=time.time(),
             error=f"예상치 못한 오류: {e}")


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

    @app.get("/")
    def home():
        # 대문(소개) — 손님이 처음 보는 화면. 여기서 '자막 만들기'로 도구(/app)로 이동.
        return send_from_directory(FRONTEND_DIR, "home.html")

    @app.get("/app")
    def app_tool():
        # 실제 자막 도구
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.post("/api/convert")
    def convert():
        from .youtube_parser import parse_video_id

        data = request.get_json(silent=True) or {}
        url = (data.get("url") or "").strip()
        include_ts = bool(data.get("timestamps", True))
        model_size = data.get("model", "medium")
        if model_size not in {"tiny", "base", "small", "medium", "large-v3"}:
            model_size = "medium"

        if not parse_video_id(url):
            return jsonify(error="유튜브 영상 주소가 아닙니다. URL을 확인해 주세요."), 400

        _purge_old()
        job_id = uuid.uuid4().hex
        with _lock:
            _jobs[job_id] = {
                "stage": "시작", "percent": 0, "detail": "변환을 시작합니다",
                "done": False, "error": None, "result": None,
                "started": time.time(), "title": "자막",
            }
        threading.Thread(
            target=_worker, args=(job_id, url, include_ts, model_size), daemon=True
        ).start()
        return jsonify(job_id=job_id), 202

    @app.get("/api/lan")
    def lan():
        """폰 접속 모드일 때, 폰에서 열 주소와 QR 코드(SVG)를 준다.
        app.py 가 YSC_HOST=0.0.0.0 로 켜지면 환경변수 YSC_LAN_URL 을 채운다.
        QR 스캔 한 번이면 폰에서 바로 열려 — IP 타이핑이 필요 없다(친절 코딩)."""
        import os
        url = os.environ.get("YSC_LAN_URL", "")
        if not url:
            return jsonify(enabled=False)
        qr_svg = ""
        try:
            import io
            import segno
            buf = io.BytesIO()
            segno.make(url, error="m").save(buf, kind="svg", scale=6, border=2,
                                            dark="#333333", light="#FFFFFF")
            qr_svg = buf.getvalue().decode("utf-8")
        except Exception:
            qr_svg = ""  # QR 실패해도 주소는 보여준다
        return jsonify(enabled=True, url=url, qr=qr_svg)

    @app.get("/api/progress/<job_id>")
    def progress(job_id: str):
        with _lock:
            j = _jobs.get(job_id)
            if j is None:
                return jsonify(error="작업을 찾을 수 없습니다 (만료되었거나 잘못된 주소)."), 404
            out = {
                "stage": j["stage"], "percent": j["percent"], "detail": j["detail"],
                "done": j["done"], "error": j["error"],
                "elapsed": round(time.time() - j["started"], 1),
                "result": j["result"],
            }
        return jsonify(out)

    return app
