from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree


root = Path(__file__).resolve().parents[1]
pages = json.loads((root / "content/pages.json").read_text(encoding="utf-8-sig"))
toc = json.loads((root / "content/toc.json").read_text(encoding="utf-8-sig"))
issues: list[str] = []

hrefs = [entry["href"] for entry in pages]
section_ids = [entry["section_id"] for entry in pages]
if len(hrefs) != len(set(hrefs)):
    issues.append("Duplicate href in pages.json")
if len(section_ids) != len(set(section_ids)):
    issues.append("Duplicate section_id in pages.json")

for position, entry in enumerate(pages, start=1):
    path = root / entry["href"]
    if not path.is_file():
        issues.append(f"Missing manifest HTML: {entry['href']}")
        continue
    source = path.read_text(encoding="utf-8-sig")
    title = re.search(r'<meta\s+name="title-id"\s+content="([^"]+)"', source)
    index = re.search(r'<meta\s+name="page-section-id"\s+content="([^"]+)"', source)
    if not title or title.group(1) != entry["section_id"]:
        issues.append(f"title-id mismatch: {entry['href']}")
    if not index or index.group(1) != str(position):
        issues.append(f"page-section-id mismatch: {entry['href']} expected {position}")

for item in toc:
    if item["href"] not in hrefs:
        issues.append(f"TOC href missing from pages.json: {item['href']}")
    path = root / item["href"]
    if not path.is_file():
        issues.append(f"TOC file missing: {item['href']}")
    elif item["chapter_id"] not in path.read_text(encoding="utf-8-sig"):
        issues.append(f"TOC chapter_id absent from HTML: {item['chapter_id']}")

tree = ElementTree.parse(root / "imsmanifest.xml")
namespace = {"ims": "http://www.imsproject.org/xsd/imscp_rootv1p1p2"}
ims_hrefs = [node.attrib["href"] for node in tree.findall(".//ims:file", namespace)]
for href in hrefs:
    if href not in ims_hrefs:
        issues.append(f"HTML missing from imsmanifest.xml: {href}")

print(json.dumps({
    "reading_order_entries": len(pages),
    "toc_entries": len(toc),
    "ims_html_entries": len([href for href in ims_hrefs if href.endswith('.html')]),
    "issues": len(issues),
}, indent=2))
for issue in issues:
    print(issue)
raise SystemExit(1 if issues else 0)
