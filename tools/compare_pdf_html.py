from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "KISWAHILI LENYE MABORESHO YOTE.pdf"
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"


class IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str | None] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        data_id = values.get("data-id")
        self.stack.append(data_id)
        if data_id and tag not in {"section", "img"}:
            self.ids.append(data_id)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        data_id = values.get("data-id")
        if data_id and tag not in {"section", "img"}:
            self.ids.append(data_id)

    def handle_endtag(self, tag: str) -> None:
        if self.stack:
            self.stack.pop()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"for online reading only", " ", value)
    value = re.sub(r"kiswahili lenye maboresho yote\.indd\s*\d*", " ", value)
    value = re.sub(r"12/09/2025\s*13:22", " ", value)
    value = re.sub(r"\[\[blank:[^]]+\]\]", " ", value)
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def tokens(value: str) -> list[str]:
    return normalize(value).split()


def main() -> None:
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8-sig"))
    reader = PdfReader(PDF)
    html_by_page: dict[int, list[Path]] = defaultdict(list)
    for path in ROOT.glob("pg*_sec*.html"):
        match = re.match(r"pg(\d{3})_", path.name)
        if match:
            html_by_page[int(match.group(1))].append(path)
    html_by_page[1].append(ROOT / "index.html")

    results: list[dict[str, object]] = []
    for page_number in range(1, len(reader.pages) + 1):
        pdf_text = reader.pages[page_number - 1].extract_text() or ""
        ordered_ids: list[str] = []
        seen: set[str] = set()
        for path in sorted(html_by_page.get(page_number, [])):
            parser = IdParser()
            parser.feed(path.read_text(encoding="utf-8-sig"))
            for data_id in parser.ids:
                if data_id not in seen and data_id in texts and str(texts[data_id]).strip():
                    ordered_ids.append(data_id)
                    seen.add(data_id)
        html_text = " ".join(str(texts[data_id]) for data_id in ordered_ids)
        pdf_norm = normalize(pdf_text)
        html_norm = normalize(html_text)
        pdf_tokens = set(tokens(pdf_text))
        html_tokens = set(tokens(html_text))
        overlap = len(pdf_tokens & html_tokens) / max(1, len(pdf_tokens))
        sequence = SequenceMatcher(None, pdf_norm, html_norm, autojunk=False).ratio()
        missing_common = sorted(
            (token for token in pdf_tokens - html_tokens if len(token) >= 5),
            key=lambda token: (-tokens(pdf_text).count(token), token),
        )[:30]
        results.append(
            {
                "page": page_number,
                "html_files": [path.name for path in sorted(html_by_page.get(page_number, []))],
                "data_ids": len(ordered_ids),
                "pdf_chars": len(pdf_norm),
                "html_chars": len(html_norm),
                "pdf_token_coverage": round(overlap, 4),
                "sequence_ratio": round(sequence, 4),
                "missing_pdf_tokens_sample": missing_common,
            }
        )

    ranked = sorted(results, key=lambda item: (item["pdf_token_coverage"], item["sequence_ratio"]))
    report = {
        "summary": {
            "pdf_pages": len(reader.pages),
            "pages_with_html": sum(bool(item["html_files"]) for item in results),
            "coverage_below_80_percent": sum(item["pdf_token_coverage"] < 0.8 for item in results),
            "coverage_below_60_percent": sum(item["pdf_token_coverage"] < 0.6 for item in results),
        },
        "lowest_coverage_pages": ranked[:30],
        "pages": results,
    }
    output = ROOT / "tmp" / "pdf-html-comparison.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    for item in ranked[:30]:
        print(
            f"pg{item['page']:03}: coverage={item['pdf_token_coverage']:.1%} "
            f"sequence={item['sequence_ratio']:.1%} ids={item['data_ids']} "
            f"files={','.join(item['html_files'])}"
        )
    print(f"report={output}")


if __name__ == "__main__":
    main()
