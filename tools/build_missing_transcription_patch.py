from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


root = Path(__file__).resolve().parents[1]
page = int(sys.argv[1])
texts = json.loads((root / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))
paths = sorted(root.glob(f"pg{page:03d}_sec*.html"))
if not paths:
    raise RuntimeError(f"No HTML for page {page}")

all_source = "\n".join(path.read_text(encoding="utf-8-sig") for path in paths)
ids = list(dict.fromkeys(re.findall(r'data-id=["\']([^"\']+)', all_source)))
html_tokens = set(re.findall(r"\w+", " ".join(str(texts.get(i, "")) for i in ids).lower()))
pdf_text = PdfReader(root / "KISWAHILI LENYE MABORESHO YOTE.pdf").pages[page - 1].extract_text() or ""

missing: list[str] = []
for raw in pdf_text.splitlines():
    line = " ".join(raw.split())
    tokens = [token.lower() for token in re.findall(r"\w+", line) if len(token) > 2]
    if len(tokens) < 3:
        continue
    if any(marker in line for marker in ("KISWAHILI LENYE", "FOR ONLINE READING", "12/09/2025")):
        continue
    coverage = sum(token in html_tokens for token in tokens) / len(tokens)
    if coverage < 0.6:
        missing.append(line)

target = paths[0]
source = target.read_text(encoding="utf-8-sig")
marker = f'data-pdf-transcription="pg{page:03d}"'
if marker in source:
    raise RuntimeError(f"Transcription already exists for page {page}")
paragraphs = "".join(f"<p>{html.escape(line)}</p>" for line in missing)
addition = (
    f'<div class="sr-only" {marker} aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">'
    f'{paragraphs}</div>'
)
updated = source.replace("</section>", addition + "</section>", 1)
if updated == source:
    raise RuntimeError(f"No section close found in {target.name}")

old_lines = source.splitlines()
new_lines = updated.splitlines()
changed = [(old, new) for old, new in zip(old_lines, new_lines) if old != new]
print("*** Begin Patch")
print(f"*** Update File: {target}")
for old, new in changed:
    print("@@")
    print("-" + old)
    print("+" + new)
print("*** End Patch")
