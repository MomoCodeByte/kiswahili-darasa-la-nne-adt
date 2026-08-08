"""Remove the unwanted 'Mwendelezo wa habari' block from navigation page 53."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_IDS = [f"pg046_n{number:04d}" for number in range(2, 6)]


def remove_json_keys(path: Path, keys: set[str]) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in keys:
        data.pop(key, None)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    page_path = ROOT / "pg046_sec001.html"
    source = page_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'<aside\b[^>]*aria-labelledby="pg046-cont"[^>]*>.*?</aside>',
        "",
        source,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("The Mwendelezo wa habari block was not found exactly once")
    page_path.write_text(updated, encoding="utf-8")

    keys = set(TEXT_IDS)
    keys.update(f"{data_id}_easy_read" for data_id in TEXT_IDS)
    remove_json_keys(ROOT / "content" / "i18n" / "sw-TZ" / "texts.json", keys)
    remove_json_keys(ROOT / "content" / "i18n" / "sw-TZ" / "audios.json", keys)
    remove_json_keys(
        ROOT / "content" / "i18n" / "sw-TZ" / "timecode" / "timecode_output.json",
        keys,
    )

    audio_dir = ROOT / "content" / "i18n" / "sw-TZ" / "audio"
    deleted = 0
    for data_id in keys:
        audio_path = audio_dir / f"{data_id}.mp3"
        if audio_path.exists():
            audio_path.unlink()
            deleted += 1

    print(f"Removed the continuation block and {deleted} orphaned audio files.")


if __name__ == "__main__":
    main()
