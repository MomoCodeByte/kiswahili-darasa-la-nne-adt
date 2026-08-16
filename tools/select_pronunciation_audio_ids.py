"""Select narration IDs affected by the approved Kiswahili pronunciation rules."""

from __future__ import annotations

import json
import re
from pathlib import Path

from regenerate_sw_audio import spoken_text


ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "content" / "i18n" / "sw-TZ"
TARGET = re.compile(
    r"\b(?:TET|UDOM|UDSM|DUCE|Mt|Bi|Bw|Dr|Prof|VI|V|http|https|www|go|tz)\b"
    r"|s\s*\.\s*l\s*\.\s*p|[+/]|(?<!\w)[-–—](?!\w)",
    flags=re.IGNORECASE,
)
FOOTER = re.compile(
    r"^FOR\s+ONLINE\s+READING\s+ONLY$"
    r"|KISWAHILI\s+LENYE\s+MABORESHO\s+YOTE\.indd"
    r"|^\d{1,2}/\d{1,2}/20\d{2}\s+\d{1,2}:\d{2}$",
    flags=re.IGNORECASE,
)


def main() -> None:
    texts = json.loads((LOCALE / "texts.json").read_text(encoding="utf-8"))
    audios = json.loads((LOCALE / "audios.json").read_text(encoding="utf-8"))
    selected = []
    pronunciations = {}
    skipped_footer = []
    for data_id in audios:
        text = texts.get(data_id, "").strip()
        if FOOTER.search(text):
            skipped_footer.append(data_id)
            continue
        if TARGET.search(text):
            selected.append(data_id)
            pronunciations[data_id] = spoken_text(text)

    ids_path = ROOT / "tools" / "pronunciation_audio_ids.txt"
    ids_path.write_text("\n".join(selected) + "\n", encoding="utf-8")
    (LOCALE / "pronunciations.json").write_text(
        json.dumps(pronunciations, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"SELECTED={len(selected)} FOOTER_SKIPPED={len(skipped_footer)} "
        f"PRONUNCIATIONS={len(pronunciations)}"
    )


if __name__ == "__main__":
    main()
