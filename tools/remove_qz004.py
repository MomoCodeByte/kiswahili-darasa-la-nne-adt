"""Remove navigation page 45 (qz004) and all of its bundled resources."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUIZ = "qz004"
QUIZ_IDS = {
    "qz004_que",
    "qz004_o0", "qz004_o0_exp",
    "qz004_o1", "qz004_o1_exp",
    "qz004_o2", "qz004_o2_exp",
}

def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))

def write_json(relative: str, value) -> None:
    (ROOT / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

pages = load_json("content/pages.json")
pages = [item for item in pages if item.get("section_id") != QUIZ]
write_json("content/pages.json", pages)

for relative in (
    "content/i18n/sw-TZ/texts.json",
    "content/i18n/sw-TZ/audios.json",
    "content/i18n/sw-TZ/timecode/timecode_output.json",
):
    data = load_json(relative)
    for data_id in QUIZ_IDS:
        data.pop(data_id, None)
    write_json(relative, data)

manifest = ROOT / "imsmanifest.xml"
manifest_text = manifest.read_text(encoding="utf-8-sig")
manifest_text = manifest_text.replace('      <file href="qz004.html"/>\n', "")
manifest.write_text(manifest_text, encoding="utf-8")

scorm = ROOT / "assets/scorm.js"
scorm_text = scorm.read_text(encoding="utf-8-sig")
scorm_text = scorm_text.replace('"qz004",', "")
scorm.write_text(scorm_text, encoding="utf-8")

preloader = ROOT / "assets/offline-preloader.js"
source = preloader.read_text(encoding="utf-8-sig")
marker = "  var INLINE = "
start = source.index(marker) + len(marker)
old_inline, consumed = json.JSONDecoder().raw_decode(source[start:])
keys = [key for key in old_inline if key != "./qz004.html"]
inline = {}
for key in keys:
    path = ROOT / key.removeprefix("./")
    if not path.is_file():
        continue
    if path.suffix.lower() == ".json":
        inline[key] = json.loads(path.read_text(encoding="utf-8-sig"))
    else:
        inline[key] = path.read_text(encoding="utf-8-sig")
payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
preloader.write_text(source[:start] + payload + source[start + consumed:], encoding="utf-8")

for data_id in QUIZ_IDS:
    (ROOT / "content/i18n/sw-TZ/audio" / f"{data_id}.mp3").unlink(missing_ok=True)
(ROOT / "qz004.html").unlink(missing_ok=True)

print(json.dumps({
    "removed_page": QUIZ,
    "remaining_pages": len(pages),
    "removed_audio_files": len(QUIZ_IDS),
}, indent=2))

