"""Refresh inline offline resources after sign-language post-processing."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    preloader_path = ROOT / "assets" / "offline-preloader.js"
    source = preloader_path.read_text(encoding="utf-8-sig")
    marker = "var INLINE = "
    start = source.index(marker) + len(marker)
    inline, consumed = json.JSONDecoder().raw_decode(source[start:])

    pages = json.loads((ROOT / "content" / "pages.json").read_text(encoding="utf-8"))
    inline["./assets/config.json"] = json.loads(
        (ROOT / "assets" / "config.json").read_text(encoding="utf-8")
    )
    inline["./assets/sign-language-tts-compat.js"] = (
        ROOT / "assets" / "sign-language-tts-compat.js"
    ).read_text(encoding="utf-8")
    inline["./content/pages.json"] = pages
    inline["./content/i18n/sw-TZ/videos.json"] = json.loads(
        (ROOT / "content" / "i18n" / "sw-TZ" / "videos.json").read_text(
            encoding="utf-8"
        )
    )
    for page in pages:
        inline[f"./{page['href']}"] = (ROOT / page["href"]).read_text(encoding="utf-8")

    payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
    preloader_path.write_text(
        source[:start] + payload + source[start + consumed :], encoding="utf-8"
    )
    print(f"Refreshed {len(inline)} offline resources")


if __name__ == "__main__":
    main()
