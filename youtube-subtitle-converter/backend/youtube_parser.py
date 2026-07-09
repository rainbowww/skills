"""YouTube URL 파싱 + 오디오 추출 (yt-dlp).

원안 문서와 달리 FFmpegExtractAudio 후처리를 쓰지 않는다 — 그 경로는 시스템
ffmpeg 설치가 필요하다. faster-whisper는 PyAV(ffmpeg 라이브러리 내장)로
m4a/webm 원본 오디오를 직접 디코딩하므로, 받은 파일을 그대로 넘기면 된다.
"""
from __future__ import annotations

import re
from pathlib import Path

_VIDEO_ID_PATTERNS = [
    r"(?:v=|/)([\w-]{11})(?:[?&#]|$)",
    r"youtu\.be/([\w-]{11})",
    r"shorts/([\w-]{11})",
    r"embed/([\w-]{11})",
]


def parse_video_id(url: str) -> str | None:
    """유튜브 URL에서 11자리 영상 ID를 추출한다. 실패 시 None."""
    url = url.strip()
    for pattern in _VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_audio(
    url: str,
    output_dir: str | Path,
    cookies_from_browser: str | None = None,
) -> tuple[Path, str]:
    """영상의 오디오 트랙을 output_dir에 내려받는다.

    Args:
        cookies_from_browser: 유튜브 "봇 확인" 차단을 만나면 브라우저 쿠키로 우회.
            "chrome" / "edge" / "firefox" 등. 데이터센터 IP(클라우드·CI)에서 흔히 필요하고,
            일반 가정·학교 IP에서는 대개 불필요.
    Returns:
        (오디오 파일 경로, 영상 제목)
    Raises:
        ValueError: URL에서 영상 ID를 찾지 못한 경우
        RuntimeError: 다운로드 실패 (봇 차단 시 안내 메시지 포함)
    """
    import yt_dlp  # 무거운 import는 지연 로딩

    video_id = parse_video_id(url)
    if not video_id:
        raise ValueError("유튜브 영상 주소가 아닙니다. URL을 확인해 주세요.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(output_dir / f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_from_browser,)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "not a bot" in msg or "Sign in to confirm" in msg:
            raise RuntimeError(
                "유튜브가 봇 확인을 요구했습니다. 로그인된 브라우저의 쿠키가 필요합니다 — "
                "CLI에서는 --cookies chrome (또는 edge/firefox) 옵션을 붙여 다시 시도하세요. "
                "가정·학교 등 일반 네트워크에서는 대개 필요 없습니다."
            ) from e
        raise RuntimeError(f"영상 다운로드 실패: {e}") from e

    title = info.get("title", "Untitled")
    audio_path = Path(ydl.prepare_filename(info))
    if not audio_path.exists():
        # 확장자가 달라진 경우 실제 파일 탐색
        candidates = list(output_dir.glob(f"{video_id}.*"))
        if not candidates:
            raise RuntimeError("다운로드된 오디오 파일을 찾지 못했습니다.")
        audio_path = candidates[0]
    return audio_path, title
