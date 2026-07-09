"""faster-whisper 한국어 음성 인식 엔진."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_model_cache: dict[str, object] = {}

# 진행 콜백 타입: (완료초, 전체초, 인식된문장수) -> None
ProgressCb = Callable[[float, float, int], None]


@dataclass
class Segment:
    """인식된 문장 한 개 (시작 시각 초 단위 + 텍스트)."""
    start: float
    text: str


def transcribe_audio(
    audio_path: str | Path,
    model_size: str = "medium",
    language: str = "ko",
    progress_cb: "ProgressCb | None" = None,
    model_cb: "Callable[[], None] | None" = None,
) -> list[Segment]:
    """오디오 파일을 문장 단위 자막 세그먼트 리스트로 변환한다.

    model_size: tiny/base/small/medium/large-v3 — 한국어 실사용은 medium 이상 권장,
    tiny는 빠른 동작 확인용.
    progress_cb: 세그먼트가 인식될 때마다 (현재까지초, 전체길이초, 문장수)로 호출.
        전체길이초를 알면 현재/전체로 진행률(%)을 계산할 수 있다.
    model_cb: 모델을 새로 준비(첫 실행 시 내려받기)하기 직전에 한 번 호출 —
        "음성 인식 준비 중" 안내용.
    """
    from faster_whisper import WhisperModel  # 무거운 import는 지연 로딩

    if model_size not in _model_cache:
        if model_cb:
            model_cb()  # 처음이면 모델 내려받기(수 분) — 안내 표시용
        _model_cache[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    model = _model_cache[model_size]

    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
    )
    total = float(getattr(info, "duration", 0.0) or 0.0)
    out: list[Segment] = []
    for s in segments:  # 제너레이터 소비 = 실제 인식 진행
        out.append(Segment(start=s.start, text=s.text))
        if progress_cb:
            progress_cb(float(getattr(s, "end", s.start) or s.start), total, len(out))
    return out
