#!/usr/bin/env python3
# 대상(실행 위치): 🟩 리눅스/macOS 터미널 또는 윈도우(python 설치 후) — 사람이 직접 실행
"""자막 변환기 CLI — 유튜브 URL → 한국어 자막 .txt

사용 예:
  python cli.py "https://youtu.be/XXXX" -t            # 타임스탬프 포함
  python cli.py "https://youtu.be/XXXX" -o out.txt    # 저장 경로 지정
  python cli.py "https://youtu.be/XXXX" --model small # 모델 크기 선택
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from backend.youtube_parser import download_audio, parse_video_id
from backend.transcriber import transcribe_audio
from backend.formatter import format_subtitles, safe_filename


def main() -> int:
    parser = argparse.ArgumentParser(
        description="유튜브 영상 목소리를 한국어 자막 .txt로 변환합니다.",
    )
    parser.add_argument("url", help="유튜브 영상 URL")
    parser.add_argument(
        "-t", "--timestamps", action="store_true",
        help="각 문장 앞에 [MM:SS] 타임스탬프를 붙입니다",
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="저장할 .txt 경로 (기본: 영상제목.txt)",
    )
    parser.add_argument(
        "--model", default="medium",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper 모델 크기 (한국어 실사용 권장: medium 이상, 기본: medium)",
    )
    args = parser.parse_args()

    if not parse_video_id(args.url):
        print("오류: 유튜브 영상 주소가 아닙니다. URL을 확인해 주세요.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="subconv_") as tmp:
        print("[1/3] 영상 오디오 내려받는 중...")
        try:
            audio_path, title = download_audio(args.url, tmp)
        except (ValueError, RuntimeError) as e:
            print(f"오류: {e}", file=sys.stderr)
            return 1
        print(f"      제목: {title}")

        print(f"[2/3] 목소리를 자막으로 변환 중... (모델: {args.model} — 영상 길이에 따라 수 분 걸릴 수 있음)")
        segments = transcribe_audio(audio_path, model_size=args.model)

    print("[3/3] 텍스트 가공 및 저장...")
    text = format_subtitles(segments, include_timestamp=args.timestamps)
    out = Path(args.output) if args.output else Path(f"{safe_filename(title)}.txt")
    out.write_text(f"# {title}\n\n{text}\n", encoding="utf-8")
    print(f"완료 ✅  {out.resolve()}  ({len(segments)}문장)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
