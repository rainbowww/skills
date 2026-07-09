"""타임스탬프 포맷팅 + TXT 텍스트 생성."""
from __future__ import annotations

import re


def _stamp(seconds: float) -> str:
    """초 → [MM:SS] (1시간 이상이면 [H:MM:SS])."""
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m:02d}:{s:02d}]"


def format_subtitles(segments, include_timestamp: bool = True) -> str:
    """세그먼트 리스트를 최종 자막 텍스트로 가공한다.

    include_timestamp=True  → 각 줄 앞에 [MM:SS] 접두사
    include_timestamp=False → 순수 텍스트만 줄바꿈
    """
    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if include_timestamp:
            lines.append(f"{_stamp(seg.start)} {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def safe_filename(title: str, max_len: int = 80) -> str:
    """영상 제목을 파일명으로 안전하게 변환한다."""
    name = re.sub(r'[\\/:*?"<>|]', "_", title).strip() or "subtitles"
    return name[:max_len]
