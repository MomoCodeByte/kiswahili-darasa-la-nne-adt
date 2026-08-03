from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from html.parser import HTMLParser


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.metas: dict[str, str] = {}
        self.sections = 0
        self.has_main = False
        self.headings: list[int] = []
        self.data_ids: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.activity_attrs: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "meta" and values.get("name"):
            self.metas[values["name"]] = values.get("content", "")
        if tag == "section":
            self.sections += 1
            if values.get("role") == "activity":
                self.activity_attrs = values
        if tag == "main":
            self.has_main = True
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if values.get("data-id"):
            self.data_ids.append((tag, values["data-id"]))
        if tag == "img":
            self.images.append(values)


def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> None:
    pages = load_json(ROOT / "content" / "pages.json")
    texts = load_json(I18N / "texts.json")
    audios = load_json(I18N / "audios.json")
    timecodes = load_json(I18N / "timecode" / "timecode_output.json")
    glossary = load_json(I18N / "glossary.json")

    issues: list[dict[str, object]] = []
    html_ids: dict[str, list[str]] = defaultdict(list)
    manifest_hrefs = [entry["href"] for entry in pages]
    manifest_section_ids = [entry["section_id"] for entry in pages]

    def add(kind: str, file: str, detail: str, severity: str = "error") -> None:
        issues.append({"severity": severity, "kind": kind, "file": file, "detail": detail})

    for index, entry in enumerate(pages, start=1):
        href = entry["href"]
        path = ROOT / href
        if not path.is_file():
            add("missing_manifest_html", href, f"Manifest position {index}")
            continue
        source = path.read_text(encoding="utf-8-sig")
        parser = PageParser()
        parser.feed(source)
        actual_title = parser.metas.get("title-id")
        actual_position = parser.metas.get("page-section-id")
        if actual_title != entry["section_id"]:
            add("section_id_mismatch", href, f"manifest={entry['section_id']!r}, html={actual_title!r}")
        if actual_position != str(index):
            add("page_section_id_mismatch", href, f"expected={index}, html={actual_position!r}")
        if not parser.sections:
            add("missing_section", href, "No section element")
        if not parser.has_main:
            add("missing_main", href, "No main landmark")
        h1_count = parser.headings.count(1)
        if not h1_count:
            add("missing_h1", href, "No h1", "warning")
        elif h1_count > 1:
            add("multiple_h1", href, f"Found {h1_count} h1 elements", "warning")

        for prior, current in zip(parser.headings, parser.headings[1:]):
            if current > prior + 1:
                add("heading_level_skip", href, f"h{prior} followed by h{current}", "warning")

        seen_local: Counter[str] = Counter()
        for tag_name, data_id in parser.data_ids:
            if tag_name == "section":
                continue
            escaped_id = re.escape(data_id)
            is_empty = bool(re.search(
                rf'<([a-zA-Z0-9]+)\b[^>]*data-id=["\']{escaped_id}["\'][^>]*>\s*</\1>',
                source,
                flags=re.S,
            ))
            if is_empty and data_id not in texts:
                continue
            seen_local[data_id] += 1
            html_ids[data_id].append(href)
            if tag_name == "img":
                image = next((item for item in parser.images if item.get("data-id") == data_id), {})
                src = image.get("src")
                if not src or not (ROOT / src).is_file():
                    add("missing_image_file", href, f"{data_id}: {src!r}")
                if data_id not in texts or not str(texts.get(data_id, "")).strip():
                    add("missing_image_description", href, data_id)
            elif data_id not in texts:
                add("html_id_missing_text", href, data_id)
        for data_id, count in seen_local.items():
            if count > 1:
                add("duplicate_data_id_in_html", href, f"{data_id}: {count}", "warning")

        for image in parser.images:
            if not image.get("data-id"):
                add("image_without_data_id", href, image.get("src", "<no src>"))

        if href.startswith("qz"):
            activity = parser.activity_attrs
            if activity is None:
                add("quiz_missing_activity_role", href, "No role=activity section")
            else:
                try:
                    correct = json.loads(activity.get("data-correct-answers", ""))
                except Exception:
                    add("quiz_invalid_correct_answers", href, "Invalid data-correct-answers JSON")
                    correct = {}
                if sum(value is True for value in correct.values()) != 1:
                    add("quiz_correct_answer_count", href, f"Expected one correct option; got {correct}")

    html_files = {path.name for path in ROOT.glob("*.html")}
    for extra in sorted(html_files - set(manifest_hrefs)):
        add("html_not_in_manifest", extra, "Root HTML is not in pages.json", "warning")
    if len(manifest_hrefs) != len(set(manifest_hrefs)):
        add("duplicate_manifest_href", "content/pages.json", "Duplicate href entries")
    if len(manifest_section_ids) != len(set(manifest_section_ids)):
        add("duplicate_manifest_section_id", "content/pages.json", "Duplicate section_id entries")

    for data_id in sorted(html_ids):
        if data_id not in audios:
            add("html_id_missing_audio_mapping", html_ids[data_id][0], data_id, "warning")
    for data_id, filename in audios.items():
        if data_id not in texts:
            add("audio_id_missing_text", "content/i18n/sw-TZ/audios.json", data_id)
        if not (I18N / "audio" / filename).is_file():
            add("missing_audio_file", "content/i18n/sw-TZ/audios.json", f"{data_id}: {filename}")
    for data_id in texts:
        auxiliary = (
            data_id.endswith("_easy_read")
            or data_id.endswith("_exp")
            or "_ans_" in data_id
            or "_ans_item-" in data_id
            or str(texts[data_id]).strip(" _") == ""
        )
        if data_id not in html_ids and not data_id.startswith("gl") and not auxiliary:
            add("text_id_not_used_in_html", "content/i18n/sw-TZ/texts.json", data_id, "warning")
    for word, entry in glossary.items():
        if not isinstance(entry, dict) or not entry.get("definition"):
            add("invalid_glossary_entry", "content/i18n/sw-TZ/glossary.json", word)

    report = {
        "summary": {
            "manifest_entries": len(pages),
            "html_files": len(html_files),
            "unique_html_data_ids": len(html_ids),
            "text_ids": len(texts),
            "audio_mappings": len(audios),
            "audio_files": len(list((I18N / "audio").glob("*.mp3"))),
            "timecode_entries": len(timecodes),
            "glossary_entries": len(glossary),
            "errors": sum(i["severity"] == "error" for i in issues),
            "warnings": sum(i["severity"] == "warning" for i in issues),
        },
        "issue_counts": Counter(i["kind"] for i in issues),
        "issues": issues,
    }
    output = ROOT / "tmp" / "adt-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(json.dumps(report["issue_counts"], ensure_ascii=False, indent=2))
    print(f"report={output}")


if __name__ == "__main__":
    main()
