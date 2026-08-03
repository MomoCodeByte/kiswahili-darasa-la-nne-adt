from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content" / "pages.json").read_text(encoding="utf-8-sig"))
old = 'src="./assets/offline-preloader.js?v=4"'
new = 'src="./assets/offline-preloader.js?v=5"'
changed = 0
for entry in pages:
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    updated = source.replace(old, new)
    if updated != source:
        path.write_text(updated, encoding="utf-8")
        changed += 1
    elif new not in source:
        raise SystemExit(f"offline preloader reference missing: {entry['href']}")
print(f"versioned references={changed}/{len(pages)}")
