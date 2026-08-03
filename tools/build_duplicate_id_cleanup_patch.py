from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


root = Path(__file__).resolve().parents[1]
report = json.loads((root / "tmp/adt-audit.json").read_text(encoding="utf-8"))
target = sys.argv[1]
ids_by_file: dict[str, list[str]] = defaultdict(list)
for issue in report["issues"]:
    if issue["kind"] == "duplicate_data_id_in_html":
        ids_by_file[issue["file"]].append(issue["detail"].split(":", 1)[0])

path = root / target
source = path.read_text(encoding="utf-8-sig")
updated = source
for data_id in ids_by_file[target]:
    attr = f' data-id="{data_id}"'
    starts = [match.start() for match in re.finditer(re.escape(attr), updated)]
    if len(starts) < 2:
        raise RuntimeError(f"Expected duplicate {data_id} in {target}")
    keep_index = len(starts) - 1 if target == "pg022_sec001.html" else 0
    pieces: list[str] = []
    cursor = 0
    occurrence = 0
    for match in re.finditer(re.escape(attr), updated):
        pieces.append(updated[cursor:match.start()])
        pieces.append(attr if occurrence == keep_index else "")
        cursor = match.end()
        occurrence += 1
    pieces.append(updated[cursor:])
    updated = "".join(pieces)

if target == "pg091_sec001.html":
    updated = updated.replace("max-sm:hidden hidden\">Fikiri", "max-sm:hidden\">Fikiri", 1)

old_lines = source.splitlines()
new_lines = updated.splitlines()
changed = [(old, new) for old, new in zip(old_lines, new_lines) if old != new]
print("*** Begin Patch")
print(f"*** Update File: {path}")
for old, new in changed:
    print("@@")
    print("-" + old)
    print("+" + new)
print("*** End Patch")
