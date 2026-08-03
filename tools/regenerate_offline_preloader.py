from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "assets" / "offline-preloader.js"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    source = TARGET.read_text(encoding="utf-8-sig")
    marker = "var INLINE = "
    start = source.index(marker) + len(marker)
    _, consumed = json.JSONDecoder().raw_decode(source[start:])
    suffix = source[start + consumed :]

    pages = load_json(ROOT / "content" / "pages.json")
    ordered_paths = [
        "assets/config.json",
        "content/pages.json",
        "content/toc.json",
        "content/navigation/nav.html",
        *[entry["href"] for entry in pages],
        "assets/interface_translations/sw-TZ/interface_translations.json",
        "content/i18n/sw-TZ/texts.json",
        "content/i18n/sw-TZ/audios.json",
        "content/i18n/sw-TZ/videos.json",
        "content/i18n/sw-TZ/images.json",
        "content/i18n/sw-TZ/glossary.json",
        "content/i18n/sw-TZ/timecode/timecode_output.json",
    ]

    inline: dict[str, object] = {}
    for relative in ordered_paths:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        key = "./" + relative.replace("\\", "/")
        if path.suffix.lower() == ".json":
            inline[key] = load_json(path)
        else:
            inline[key] = path.read_text(encoding="utf-8-sig")

    encoded = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
    TARGET.write_text(source[:start] + encoded + suffix, encoding="utf-8")
    print(f"offline entries={len(inline)} pages={len(pages)} bytes={TARGET.stat().st_size}")


if __name__ == "__main__":
    main()
