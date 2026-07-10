"""유튜브 기존 자막(VTT) 우선 가져오기.

전략: 대부분의 유튜브 영상은 이미 자동/수동 자막(VTT)이 있고 시간 정보까지 붙어 있다.
그걸 그대로 가져오면 STT(무거운 부분)를 돌릴 필요가 없다 — 빠르고 안정적.
없거나 실패하면 호출부에서 우리 엔진(Whisper)으로 폴백한다.
"""
from __future__ import annotations

import re
import urllib.request

from .transcriber import Segment

# 한국어 계열 자막 우선순위 (ko, ko-KR, 자동생성 ko 등)
_KO_PREFIXES = ("ko",)

_TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")
_TAG = re.compile(r"<[^>]+>")


def _to_seconds(m: "re.Match") -> float:
    h, mm, ss, ms = (int(x) for x in m.groups())
    return h * 3600 + mm * 60 + ss + ms / 1000.0


def _dedupe_rolling(cues: list[Segment]) -> list[Segment]:
    """유튜브 자동자막의 '굴러가는(rolling)' 겹침 제거.
    각 자막 줄이 앞줄의 끝을 반복하므로, 앞 줄과 겹치는 단어를 빼고
    '새로 늘어난 부분'만 남긴다. (겹침이 없는 정식 자막은 그대로 통과.)
    """
    out: list[Segment] = []
    prev: list[str] = []
    for c in cues:
        words = c.text.split()
        # prev의 접미사와 words의 접두사가 겹치는 최대 길이 k
        k = 0
        for i in range(min(len(prev), len(words)), 0, -1):
            if prev[-i:] == words[:i]:
                k = i
                break
        new_words = words[k:]
        prev = words
        if new_words:  # 완전히 겹치면(새 단어 없음) 건너뜀
            out.append(Segment(start=c.start, text=" ".join(new_words)))
    return out


def parse_vtt(text: str) -> list[Segment]:
    """WEBVTT 텍스트를 (시작초, 텍스트) 세그먼트 리스트로 파싱한다.
    태그(<c>, <00:00:01.500> 등) 제거 후, 자동자막의 롤링 겹침을 제거한다.
    """
    cues: list[Segment] = []
    for block in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n").replace("\r", "\n")):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        timing_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if timing_idx is None:
            continue
        m = _TS.search(lines[timing_idx])
        if not m:
            continue
        start = _to_seconds(m)
        raw = " ".join(lines[timing_idx + 1:])
        txt = _TAG.sub("", raw)
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            cues.append(Segment(start=start, text=txt))
    return _dedupe_rolling(cues)


def _pick_vtt_url(caption_map: dict) -> str | None:
    """자막 언어맵에서 한국어 계열의 vtt URL을 고른다. 없으면 None."""
    if not caption_map:
        return None
    # 정확히 ko 계열 우선
    keys = list(caption_map.keys())
    ordered = [k for k in keys if any(k.lower().startswith(p) for p in _KO_PREFIXES)]
    for lang in ordered:
        for fmt in caption_map.get(lang, []):
            if fmt.get("ext") == "vtt" or "vtt" in (fmt.get("url", "")):
                return fmt.get("url")
    return None


def fetch_captions(url: str) -> tuple[list[Segment], str] | None:
    """유튜브의 기존 한국어 자막(VTT)을 가져와 (세그먼트, 제목)으로 반환.
    자막이 없거나 실패하면 None (→ 호출부에서 Whisper 폴백)."""
    import yt_dlp  # 지연 로딩

    opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["ko", "ko-KR", "ko-orig"],
        "subtitlesformat": "vtt",
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception:  # noqa: BLE001 — 실패는 조용히 폴백
        return None

    title = info.get("title", "자막")
    # 수동 자막 우선, 없으면 자동 자막
    vtt_url = _pick_vtt_url(info.get("subtitles") or {}) \
        or _pick_vtt_url(info.get("automatic_captions") or {})
    if not vtt_url:
        return None
    try:
        with urllib.request.urlopen(vtt_url, timeout=30) as r:
            vtt_text = r.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None
    segments = parse_vtt(vtt_text)
    if not segments:
        return None
    return segments, title
