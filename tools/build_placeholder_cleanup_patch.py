from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


root = Path(__file__).resolve().parents[1]
report = json.loads((root / "tmp/adt-audit.json").read_text(encoding="utf-8"))
by_file: dict[str, list[str]] = defaultdict(list)
for issue in report["issues"]:
    if issue["kind"] == "html_id_missing_audio_mapping":
        by_file[issue["file"]].append(issue["detail"])

updates: list[tuple[Path, str, str]] = []
for filename, ids in by_file.items():
    path = root / filename
    source = path.read_text(encoding="utf-8-sig")
    updated = source
    for data_id in ids:
        updated = updated.replace(f' data-id="{data_id}"', "")
    if updated == source:
        raise RuntimeError(f"No placeholder attributes removed from {filename}")
    updates.append((path, source, updated))

path136 = root / "pg136_sec001.html"
source136 = path136.read_text(encoding="utf-8-sig")
old136 = '<h1 class="text-[32px] leading-none font-bold text-blue-700" data-id="pg136_n0014">B.</h1>'
new136 = '<h2 class="text-[32px] leading-none font-bold text-blue-700" data-id="pg136_n0014">B.</h2>'
if old136 in source136:
    updates.append((path136, source136, source136.replace(old136, new136, 1)))

print("*** Begin Patch")
for path, source, updated in updates:
    old_lines = source.splitlines()
    new_lines = updated.splitlines()
    changed = [(old, new) for old, new in zip(old_lines, new_lines) if old != new]
    print(f"*** Update File: {path}")
    for old, new in changed:
        print("@@")
        print("-" + old)
        print("+" + new)
print("*** End Patch")
