"""faster-whisper 한국어 음성 인식 엔진."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_model_cache: dict[str, object] = {}


@dataclass
class Segment:
    """인식된 문장 한 개 (시작 시각 초 단위 + 텍스트)."""
    start: float
    text: str


def transcribe_audio(
    audio_path: str | Path,
    model_size: str = "medium",
    language: str = "ko",
) -> list[Segment]:
    """오디오 파일을 문장 단위 자막 세그먼트 리스트로 변환한다.

    model_size: tiny/base/small/medium/large-v3 — 한국어 실사용은 medium 이상 권장,
    tiny는 빠른 동작 확인용.
    """
    from faster_whisper import WhisperModel  # 무거운 import는 지연 로딩

    if model_size not in _model_cache:
        _model_cache[model_size] = WhisperModel(
            model_size, device="cpu", compute_type="int8"
        )
    model = _model_cache[model_size]

    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
    )
    return [Segment(start=s.start, text=s.text) for s in segments]
