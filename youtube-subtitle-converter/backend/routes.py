"""Flask API 라우트 — 웹 UI(A 형태)가 호출하는 백엔드."""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.post("/api/convert")
    def convert():
        from .youtube_parser import download_audio, parse_video_id
        from .transcriber import transcribe_audio
        from .formatter import format_subtitles

        data = request.get_json(silent=True) or {}
        url = (data.get("url") or "").strip()
        include_ts = bool(data.get("timestamps", True))
        model_size = data.get("model", "medium")
        if model_size not in {"tiny", "base", "small", "medium", "large-v3"}:
            model_size = "medium"

        if not parse_video_id(url):
            return jsonify(error="유튜브 영상 주소가 아닙니다. URL을 확인해 주세요."), 400

        try:
            with tempfile.TemporaryDirectory(prefix="subconv_") as tmp:
                audio_path, title = download_audio(url, tmp)
                segments = transcribe_audio(audio_path, model_size=model_size)
        except (ValueError, RuntimeError) as e:
            return jsonify(error=str(e)), 502

        text = format_subtitles(segments, include_timestamp=include_ts)
        return jsonify(title=title, text=text, sentences=len(segments))

    return app
