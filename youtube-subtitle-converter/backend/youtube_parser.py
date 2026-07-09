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


# 봇 차단 시 자동으로 시도해 볼 브라우저 목록 (설치돼 있고 쿠키가 있으면 통과)
_AUTO_COOKIE_BROWSERS = ["chrome", "edge", "firefox", "brave", "chromium", "opera", "vivaldi"]


def _is_bot_gate(msg: str) -> bool:
    return "not a bot" in msg or "Sign in to confirm" in msg


def download_audio(
    url: str,
    output_dir: str | Path,
    cookies_from_browser: str | None = None,
    auto_cookies: bool = True,
) -> tuple[Path, str]:
    """영상의 오디오 트랙을 output_dir에 내려받는다.

    봇 차단("Sign in to confirm you're not a bot")을 만나면:
      1) cookies_from_browser가 지정됐으면 그걸로 재시도
      2) auto_cookies=True(기본)면 설치된 브라우저 쿠키를 자동 탐색해 하나씩 재시도
    → 사용자가 아무 옵션을 몰라도 대개 자동으로 통과한다.

    Args:
        cookies_from_browser: 특정 브라우저 쿠키를 강제 지정("chrome"/"edge"/"firefox" 등).
        auto_cookies: 봇 차단 시 설치된 브라우저 쿠키를 자동으로 시도(기본 True).
    Returns:
        (오디오 파일 경로, 영상 제목)
    Raises:
        ValueError: URL에서 영상 ID를 찾지 못한 경우
        RuntimeError: 모든 시도 실패 (안내 메시지 포함)
    """
    import yt_dlp  # 무거운 import는 지연 로딩

    video_id = parse_video_id(url)
    if not video_id:
        raise ValueError("유튜브 영상 주소가 아닙니다. URL을 확인해 주세요.")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(output_dir / f"{video_id}.%(ext)s")

    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    # 시도 순서: (지정 쿠키 or 쿠키없음) → 봇 차단이면 자동 브라우저 순회
    attempts: list[str | None] = [cookies_from_browser]
    if auto_cookies:
        attempts += [b for b in _AUTO_COOKIE_BROWSERS if b != cookies_from_browser]

    last_bot_gate = False
    for browser in attempts:
        opts = dict(base_opts)
        if browser:
            opts["cookiesfrombrowser"] = (browser,)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            title = info.get("title", "Untitled")
            audio_path = Path(ydl.prepare_filename(info))
            if not audio_path.exists():
                candidates = list(output_dir.glob(f"{video_id}.*"))
                if not candidates:
                    raise RuntimeError("다운로드된 오디오 파일을 찾지 못했습니다.")
                audio_path = candidates[0]
            return audio_path, title
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if _is_bot_gate(msg):
                last_bot_gate = True
                continue  # 다음 브라우저 쿠키로 자동 재시도
            # 봇 차단이 아닌 다른 오류(쿠키 브라우저 미설치 등)면 다음 후보로
            if browser is not None:
                continue
            raise RuntimeError(f"영상 다운로드 실패: {e}") from e

    if last_bot_gate:
        raise RuntimeError(
            "유튜브가 봇 확인을 요구했고, 설치된 브라우저의 쿠키로도 통과하지 못했습니다. "
            "크롬·엣지 등에서 youtube.com에 한 번 로그인한 뒤 다시 시도해 주세요. "
            "(가정·학교 등 일반 네트워크에서는 대개 이 단계까지 오지 않습니다.)"
        )
    raise RuntimeError("영상 다운로드에 실패했습니다. URL과 네트워크를 확인해 주세요.")
