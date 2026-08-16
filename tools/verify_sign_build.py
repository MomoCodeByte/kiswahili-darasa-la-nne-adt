"""Verify sign-language video assignment and browser media constraints."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
LANGUAGE = "sw-TZ"


def main() -> None:
    pages = json.loads((ROOT / "content" / "pages.json").read_text(encoding="utf-8"))
    videos = json.loads(
        (ROOT / "content" / "i18n" / LANGUAGE / "videos.json").read_text(
            encoding="utf-8"
        )
    )
    video_dir = ROOT / "content" / "i18n" / LANGUAGE / "video"
    files = sorted(video_dir.glob("page_*.mp4"))
    assert len(files) == len(pages) == len(videos) == 191

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    audio_tracks = []
    bad_video = []
    for path in files:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-i", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        media = result.stderr
        if re.search(r"Stream #.*Audio:", media):
            audio_tracks.append(path.name)
        if not re.search(r"Stream #.*Video: h264", media):
            bad_video.append(path.name)

    for index, page in enumerate(pages, start=1):
        assert page["page_number"] == index
        assert videos[f"video-{index}"] == f"page_{index}.mp4"
        html = (ROOT / page["href"]).read_text(encoding="utf-8")
        assert f'content="{index}"' in html
        assert "sign-language-tts-compat.js?v=2" in html

    assert not audio_tracks, f"Videos containing audio: {audio_tracks}"
    assert not bad_video, f"Non-H.264 videos: {bad_video}"
    total = sum(path.stat().st_size for path in files)
    print(
        f"PASS pages={len(pages)} videos={len(files)} audio_tracks=0 "
        f"h264={len(files)} bytes={total}"
    )


if __name__ == "__main__":
    main()
