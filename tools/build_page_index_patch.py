from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
pages = json.loads((ROOT / "content/pages.json").read_text(encoding="utf-8-sig"))
pattern = re.compile(r'(<meta\s+name="page-section-id"\s+content=")\d+("\s*/>)')
start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
end = int(sys.argv[2]) if len(sys.argv) > 2 else len(pages)

print("*** Begin Patch")
for position, entry in enumerate(pages, start=1):
    if position < start or position > end:
        continue
    path = ROOT / entry["href"]
    source = path.read_text(encoding="utf-8-sig")
    match = pattern.search(source)
    if not match:
        raise RuntimeError(f"Missing page-section-id in {path}")
    old = match.group(0)
    new = f'{match.group(1)}{position}{match.group(2)}'
    if old == new:
        continue
    print(f"*** Update File: {path}")
    print("@@")
    print(f"-{old}")
    print(f"+{new}")
print("*** End Patch")
