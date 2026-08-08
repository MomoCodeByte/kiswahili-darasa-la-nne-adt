"""Finalize navigation numbering and inclusive-language data for release."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "32"


def inclusive_texts() -> dict[str, str]:
    source = (ROOT / "assets" / "inclusive-language.js").read_text(encoding="utf-8")
    matches = re.finditer(
        r"^\s+([A-Za-z0-9_-]+):\s+'((?:\\'|[^'])*)',",
        source,
        flags=re.MULTILINE,
    )
    return {
        match.group(1): match.group(2).replace("\\'", "'")
        for match in matches
    }


def main() -> None:
    pages_path = ROOT / "content" / "pages.json"
    toc_path = ROOT / "content" / "toc.json"
    texts_path = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
    audios_path = ROOT / "content" / "i18n" / "sw-TZ" / "audios.json"
    config_path = ROOT / "assets" / "config.json"
    preloader_path = ROOT / "assets" / "offline-preloader.js"

    pages = json.loads(pages_path.read_text(encoding="utf-8"))
    toc = json.loads(toc_path.read_text(encoding="utf-8"))
    toc = [entry for entry in toc if entry.get("section_id") != "pg004_sec001"]
    texts = json.loads(texts_path.read_text(encoding="utf-8"))
    audios = json.loads(audios_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    replacements = inclusive_texts()

    if not replacements:
        raise RuntimeError("No inclusive-language replacements were found")

    numbered = 0
    for position, page in enumerate(pages, start=1):
        page_path = ROOT / page["href"]
        if not page_path.exists():
            raise FileNotFoundError(f"Navigation file is missing: {page['href']}")
        source = page_path.read_text(encoding="utf-8")
        updated, count = re.subn(
            r'(<meta name="page-section-id" content=")\d+("\s*/?>)',
            rf"\g<1>{position}\g<2>",
            source,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"Missing page-section-id in {page['href']}")
        updated = re.sub(
            r"offline-preloader\.js\?v=\d+",
            f"offline-preloader.js?v={RELEASE_VERSION}",
            updated,
        )
        updated = re.sub(
            r"inclusive-language\.js\?v=\d+",
            "inclusive-language.js?v=18",
            updated,
        )
        if "assets/book-consistency.css" not in updated:
            updated = updated.replace(
                '<link href="./assets/fonts.css" rel="stylesheet">',
                '<link href="./assets/fonts.css" rel="stylesheet">\n'
                f'    <link href="./assets/book-consistency.css?v={RELEASE_VERSION}" rel="stylesheet">',
                1,
            )
        else:
            updated = re.sub(
                r"book-consistency\.css\?v=\d+",
                f"book-consistency.css?v={RELEASE_VERSION}",
                updated,
            )
        updated = re.sub(
            r'^\s*<script src="\./assets/original-view\.js"></script>\s*\n?',
            "",
            updated,
            flags=re.MULTILINE,
        )
        page_path.write_text(updated, encoding="utf-8")
        numbered += 1

    for data_id, value in replacements.items():
        easy_id = f"{data_id}_easy_read"
        if data_id not in texts:
            raise KeyError(f"Missing source text for {data_id}")
        texts[data_id] = value
        texts[easy_id] = value
        audios.setdefault(data_id, f"{data_id}.mp3")
        audios.setdefault(easy_id, f"{easy_id}.mp3")

    config["bundleVersion"] = RELEASE_VERSION
    toc_path.write_text(
        json.dumps(toc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    texts_path.write_text(
        json.dumps(texts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    audios_path.write_text(
        json.dumps(audios, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    preloader = preloader_path.read_text(encoding="utf-8-sig")
    marker = "var INLINE = "
    start = preloader.index(marker) + len(marker)
    decoder = json.JSONDecoder()
    inline, consumed = decoder.raw_decode(preloader[start:])
    inline["./assets/config.json"] = config
    inline["./assets/book-consistency.css"] = (
        ROOT / "assets" / "book-consistency.css"
    ).read_text(encoding="utf-8")
    inline["./content/pages.json"] = pages
    inline["./content/toc.json"] = toc
    inline["./content/i18n/sw-TZ/texts.json"] = texts
    inline["./content/i18n/sw-TZ/audios.json"] = audios
    for page in pages:
        inline[f"./{page['href']}"] = (ROOT / page["href"]).read_text(encoding="utf-8")
    payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
    preloader_path.write_text(
        preloader[:start] + payload + preloader[start + consumed :],
        encoding="utf-8",
    )

    ids_path = ROOT / "tools" / "inclusive_audio_ids.txt"
    ids_path.write_text("\n".join(replacements) + "\n", encoding="utf-8")
    print(f"Renumbered {numbered} navigation entries.")
    print(f"Synchronized {len(replacements)} inclusive text IDs and Easy Read variants.")
    print(f"Wrote audio ID list to {ids_path.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
