"""Verify navigation, inclusive text/audio, and the offline bundle before release."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVED_NAV_IDS = {
    "qz001", "qz002", "qz003", "qz004", "qz005", "qz006", "qz007",
    "qz008", "qz009", "qz010", "qz011", "qz012", "qz013", "qz014",
    "qz015", "qz016", "pg111_sec001",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    pages = load_json(ROOT / "content" / "pages.json")
    toc = load_json(ROOT / "content" / "toc.json")
    texts = load_json(ROOT / "content" / "i18n" / "sw-TZ" / "texts.json")
    audios = load_json(ROOT / "content" / "i18n" / "sw-TZ" / "audios.json")
    config = load_json(ROOT / "assets" / "config.json")
    audio_dir = ROOT / "content" / "i18n" / "sw-TZ" / "audio"

    section_ids = [page["section_id"] for page in pages]
    assert len(section_ids) == len(set(section_ids)), "Duplicate navigation IDs"
    assert not REMOVED_NAV_IDS.intersection(section_ids), "Removed pages remain in navigation"

    for position, page in enumerate(pages, start=1):
        page_path = ROOT / page["href"]
        assert page_path.exists(), f"Missing page file: {page['href']}"
        html = page_path.read_text(encoding="utf-8")
        match = re.search(r'<meta name="page-section-id" content="(\d+)"', html)
        assert match and int(match.group(1)) == position, (
            f"Bad navigation number in {page['href']}: expected {position}"
        )
        assert "offline-preloader.js?v=34" in html, f"Old cache version in {page['href']}"
        assert "book-consistency.css?v=34" in html, f"Typography CSS missing in {page['href']}"
        assert "inclusive-language.js?v=20" in html, f"Old inclusive-language cache version in {page['href']}"
        assert "assets/original-view.js" not in html, f"PDF button script remains in {page['href']}"

    chapter_eight = [entry for entry in toc if entry.get("title") == "Sura ya Nane"]
    assert len(chapter_eight) == 1, "Sura ya Nane is missing or duplicated in the menu"
    assert all(entry.get("section_id") != "pg004_sec001" for entry in toc), (
        "The duplicated pg004 Sura ya Nane menu entry remains"
    )

    inclusive_source = (ROOT / "assets" / "inclusive-language.js").read_text(
        encoding="utf-8"
    )
    replacements = {
        match.group(1): match.group(2).replace("\\'", "'")
        for match in re.finditer(
            r"^\s+([A-Za-z0-9_-]+):\s+'((?:\\'|[^'])*)',",
            inclusive_source,
            flags=re.MULTILINE,
        )
    }
    assert replacements, "No inclusive-language text found"
    for data_id, value in replacements.items():
        for text_id in (data_id, f"{data_id}_easy_read"):
            assert texts.get(text_id) == value, f"Text mismatch: {text_id}"
            filename = audios.get(text_id)
            assert filename, f"Missing audio mapping: {text_id}"
            audio_path = audio_dir / filename
            assert audio_path.exists() and audio_path.stat().st_size > 1_000, (
                f"Missing or invalid audio: {text_id}"
            )

    preloader = (ROOT / "assets" / "offline-preloader.js").read_text(
        encoding="utf-8-sig"
    )
    marker = "var INLINE = "
    start = preloader.index(marker) + len(marker)
    inline, _ = json.JSONDecoder().raw_decode(preloader[start:])
    assert inline["./content/pages.json"] == pages, "Offline pages.json is stale"
    assert inline["./content/toc.json"] == toc, "Offline toc.json is stale"
    assert inline["./content/i18n/sw-TZ/texts.json"] == texts, "Offline texts are stale"
    assert inline["./content/i18n/sw-TZ/audios.json"] == audios, "Offline audio map is stale"
    assert inline["./assets/config.json"] == config, "Offline config is stale"
    assert inline["./assets/book-consistency.css"] == (
        ROOT / "assets" / "book-consistency.css"
    ).read_text(encoding="utf-8"), "Offline typography CSS is stale"
    for page in pages:
        assert inline[f"./{page['href']}"] == (ROOT / page["href"]).read_text(
            encoding="utf-8"
        ), f"Offline HTML is stale: {page['href']}"

    print(f"PASS: {len(pages)} navigation entries numbered 1-{len(pages)}.")
    print(f"PASS: {len(replacements)} inclusive IDs and 2 audio variants each.")
    print("PASS: removed pages are absent from navigation.")
    print("PASS: PDF button is removed and Sura ya Nane appears once in the menu.")
    print("PASS: offline bundle matches the release files.")


if __name__ == "__main__":
    main()
