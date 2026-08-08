"""Remove navigation pages 177, 193 and 195 with their resources."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUIZZES = {"qz014", "qz015", "qz016"}
PREFIXES = tuple(f"{quiz}_" for quiz in QUIZZES)


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def write_json(relative: str, value) -> None:
    (ROOT / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


pages = load_json("content/pages.json")
pages = [item for item in pages if item.get("section_id") not in QUIZZES]
write_json("content/pages.json", pages)

removed_ids: set[str] = set()
for relative in (
    "content/i18n/sw-TZ/texts.json",
    "content/i18n/sw-TZ/audios.json",
    "content/i18n/sw-TZ/timecode/timecode_output.json",
):
    data = load_json(relative)
    keys = {key for key in data if key.startswith(PREFIXES)}
    removed_ids.update(keys)
    for key in keys:
        data.pop(key, None)
    write_json(relative, data)

manifest = ROOT / "imsmanifest.xml"
manifest_text = manifest.read_text(encoding="utf-8-sig")
for quiz in QUIZZES:
    manifest_text = manifest_text.replace(f'      <file href="{quiz}.html"/>\n', "")
manifest.write_text(manifest_text, encoding="utf-8")

scorm = ROOT / "assets/scorm.js"
scorm_text = scorm.read_text(encoding="utf-8-sig")
match = re.search(r"var ALL_ACTIVITY_IDS = (\[[^;]*\]);", scorm_text)
if match:
    activities = json.loads(match.group(1))
    activities = [item for item in activities if item not in QUIZZES]
    scorm_text = scorm_text[:match.start(1)] + json.dumps(activities) + scorm_text[match.end(1):]
scorm.write_text(scorm_text, encoding="utf-8")

preloader = ROOT / "assets/offline-preloader.js"
source = preloader.read_text(encoding="utf-8-sig")
marker = "  var INLINE = "
start = source.index(marker) + len(marker)
old_inline, consumed = json.JSONDecoder().raw_decode(source[start:])
removed_paths = {f"./{quiz}.html" for quiz in QUIZZES}
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
    if path.stem.startswith(PREFIXES):
        path.unlink()
        deleted_audio += 1

for quiz in QUIZZES:
    (ROOT / f"{quiz}.html").unlink(missing_ok=True)

print(json.dumps({
    "removed_pages": sorted(QUIZZES),
    "remaining_pages": len(pages),
    "removed_data_ids": len(removed_ids),
    "deleted_audio_files": deleted_audio,
}, indent=2))
