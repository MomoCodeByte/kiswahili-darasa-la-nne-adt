from __future__ import annotations

import html
import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
path = root / "pg136_sec001.html"
source = path.read_text(encoding="utf-8-sig")
texts = json.loads((root / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))

needle = '<section data-section-type="activity_open_ended_answer" data-section-id="pg136_sec001" class="max-w-4xl mx-auto"><div class="flex items-baseline gap-4 mb-4 max-sm:gap-3">'
ids = [f"pg136_n{i:04d}" for i in range(3, 13)]
paragraphs = "".join(
    f'<p class="fitb-sentence text-[20px] leading-[1.45] text-black max-sm:text-[18px]" data-id="{data_id}">{html.escape(str(texts[data_id]))}</p>'
    for data_id in ids
)
replacement = (
    '<section role="article" aria-labelledby="pg136-heading" data-section-type="activity_fill_in_the_blank" '
    'data-section-id="pg136_sec001" class="max-w-4xl mx-auto">'
    '<h1 id="pg136-heading" class="sr-only">Mazoezi ya lugha</h1>'
    f'<div class="mb-8 space-y-2">{paragraphs}</div>'
    '<div class="flex items-baseline gap-4 mb-4 max-sm:gap-3">'
)
if needle not in source:
    raise RuntimeError("Expected pg136 section prefix not found")
updated = source.replace(needle, replacement, 1)

old_line = next(line for line in source.splitlines() if needle in line)
new_line = next(line for line in updated.splitlines() if replacement in line)
print("*** Begin Patch")
print(f"*** Update File: {path}")
print("@@")
print("-" + old_line)
print("+" + new_line)
print("*** End Patch")
