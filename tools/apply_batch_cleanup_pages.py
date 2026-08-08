"""Remove requested navigation pages and orphaned text/audio resources."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REMOVED_PAGES = {"qz011", "qz012", "qz013", "pg111_sec001"}
REMOVED_PREFIXES = ("qz011_", "qz012_", "qz013_", "pg111_")
REMOVED_EXACT_IDS = {
    "pg106_n0002", "pg106_n0003", "pg106_n0005", "pg106_n0006",
    "pg106_n0007", "pg106_n0008", "pg106_n0009",
    "pg106_n0002_easy_read", "pg106_n0003_easy_read",
    "pg106_n0005_easy_read", "pg106_n0006_easy_read",
    "pg106_n0007_easy_read", "pg106_n0008_easy_read",
    "pg106_n0009_easy_read",
}


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def write_json(relative: str, value) -> None:
    (ROOT / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


pages = load_json("content/pages.json")
pages = [item for item in pages if item.get("section_id") not in REMOVED_PAGES]
write_json("content/pages.json", pages)

removed_ids: set[str] = set()
for relative in (
    "content/i18n/sw-TZ/texts.json",
    "content/i18n/sw-TZ/audios.json",
    "content/i18n/sw-TZ/timecode/timecode_output.json",
):
    data = load_json(relative)
    keys = {
        key for key in data
        if key in REMOVED_EXACT_IDS or key.startswith(REMOVED_PREFIXES)
    }
    removed_ids.update(keys)
    for key in keys:
        data.pop(key, None)
    write_json(relative, data)

manifest = ROOT / "imsmanifest.xml"
manifest_text = manifest.read_text(encoding="utf-8-sig")
for page in REMOVED_PAGES:
    manifest_text = manifest_text.replace(f'      <file href="{page}.html"/>\n', "")
manifest.write_text(manifest_text, encoding="utf-8")

scorm = ROOT / "assets/scorm.js"
scorm_text = scorm.read_text(encoding="utf-8-sig")
for quiz in ("qz011", "qz012", "qz013"):
    scorm_text = scorm_text.replace(f'"{quiz}",', "").replace(f',"{quiz}"', "")
scorm.write_text(scorm_text, encoding="utf-8")

preloader = ROOT / "assets/offline-preloader.js"
source = preloader.read_text(encoding="utf-8-sig")
marker = "  var INLINE = "
start = source.index(marker) + len(marker)
old_inline, consumed = json.JSONDecoder().raw_decode(source[start:])
removed_paths = {f"./{page}.html" for page in REMOVED_PAGES}
inline = {}
for key in old_inline:
    if key in removed_paths:
        continue
    path = ROOT / key.removeprefix("./")
    if not path.is_file():
        continue
    if path.suffix.lower() == ".json":
        inline[key] = json.loads(path.read_text(encoding="utf-8-sig"))
    else:
        inline[key] = path.read_text(encoding="utf-8-sig")
payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
preloader.write_text(source[:start] + payload + source[start + consumed:], encoding="utf-8")

audio_dir = ROOT / "content/i18n/sw-TZ/audio"
deleted_audio = 0
for path in audio_dir.glob("*.mp3"):
    if path.stem in REMOVED_EXACT_IDS or path.stem.startswith(REMOVED_PREFIXES):
        path.unlink()
        deleted_audio += 1

for page in REMOVED_PAGES:
    (ROOT / f"{page}.html").unlink(missing_ok=True)

print(json.dumps({
    "removed_pages": sorted(REMOVED_PAGES),
    "remaining_pages": len(pages),
    "removed_data_ids": len(removed_ids),
    "deleted_audio_files": deleted_audio,
}, indent=2))
