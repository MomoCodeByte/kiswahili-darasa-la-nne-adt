from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
AUDIOS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "audios.json"
OUTPUT_PATH = ROOT / "assets" / "table-audio-contexts.json"


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    parent: Node | None = None
    children: list[Node] = field(default_factory=list)


class TreeParser(HTMLParser):
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


def nearest_ancestor(node: Node, tag: str) -> Node | None:
    current = node.parent
    while current is not None:
        if current.tag == tag:
            return current
        current = current.parent
    return None


def direct_table_rows(table: Node) -> list[Node]:
    return [node for node in walk(table) if node.tag == "tr" and nearest_ancestor(node, "table") is table]


def direct_row_cells(row: Node) -> list[Node]:
    return [node for node in walk(row) if node.tag in {"td", "th"} and nearest_ancestor(node, "tr") is row]


def number_word(number: int) -> str:
    ones = {
        1: "moja", 2: "mbili", 3: "tatu", 4: "nne", 5: "tano",
        6: "sita", 7: "saba", 8: "nane", 9: "tisa", 10: "kumi",
    }
    tens = {20: "ishirini", 30: "thelathini", 40: "arobaini", 50: "hamsini"}
    if number in ones:
        return ones[number]
    if 10 < number < 20:
        return f"kumi na {ones[number - 10]}"
    if 20 <= number < 60:
        base = number - number % 10
        return tens[base] if number == base else f"{tens[base]} na {ones[number - base]}"
    return str(number)


def ordinal(number: int) -> str:
    return {1: "kwanza", 2: "pili", 3: "tatu"}.get(number, number_word(number))


def row_count_phrase(number: int) -> str:
    if number == 1:
        return "mstari mmoja"
    agreements = {2: "miwili", 3: "mitatu", 4: "minne", 5: "mitano"}
    return f"mistari {agreements.get(number, number_word(number))}"


def column_count_phrase(number: int) -> str:
    return "safu moja" if number == 1 else f"safu {number_word(number)}"


def safe_span(value: str) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def add_context(contexts: dict[str, dict[str, list[str]]], text_id: str, kind: str, value: str) -> None:
    values = contexts.setdefault(text_id, {"prefix": [], "suffix": []})[kind]
    if value not in values:
        values.append(value)


def build_contexts() -> tuple[dict[str, dict[str, str]], dict[str, int]]:
    texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    audios = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))
    mapped_ids = set(texts).intersection(audios)
    raw_contexts: dict[str, dict[str, list[str]]] = {}
    page_count = table_count = cell_count = input_count = 0

    for path in sorted(ROOT.glob("*.html")):
        source = path.read_text(encoding="utf-8")
        if "<table" not in source.lower():
            continue
        parser = TreeParser()
        parser.feed(source)
        document_nodes = list(walk(parser.root))
        tables = [node for node in document_nodes if node.tag == "table"]
        if not tables:
            continue
        page_count += 1
        table_count += len(tables)

        for table_number, table in enumerate(tables, start=1):
            rows = direct_table_rows(table)
            occupied: set[tuple[int, int]] = set()
            placements: list[tuple[Node, int, int]] = []
            max_column = 0
            for row_number, row in enumerate(rows, start=1):
                column = 1
                for cell in direct_row_cells(row):
                    while (row_number, column) in occupied:
                        column += 1
                    colspan = safe_span(cell.attrs.get("colspan", "1"))
                    rowspan = safe_span(cell.attrs.get("rowspan", "1"))
                    placements.append((cell, row_number, column))
                    for future_row in range(row_number, row_number + rowspan):
                        for future_column in range(column, column + colspan):
                            occupied.add((future_row, future_column))
                    max_column = max(max_column, column + colspan - 1)
                    column += colspan

            label = "" if len(tables) == 1 else f"Jedwali la {ordinal(table_number)}. "
            first_mapped_id: str | None = None
            for cell, row_number, column in placements:
                cell_count += 1
                prefix = f"{label}Mstari wa {ordinal(row_number)}, safu ya {ordinal(column)}."
                for node in walk(cell):
                    text_id = node.attrs.get("data-id")
                    if text_id in mapped_ids:
                        if first_mapped_id is None:
                            first_mapped_id = text_id
                        add_context(raw_contexts, text_id, "prefix", prefix)
                    if node.tag in {"input", "textarea", "select"}:
                        input_count += 1

            if first_mapped_id is not None:
                orientation = (
                    f"Jedwali hili lina {row_count_phrase(len(rows))} na "
                    f"{column_count_phrase(max_column)}. Kila seli itatangaza mstari na safu yake."
                )
                prefixes = raw_contexts[first_mapped_id]["prefix"]
                if orientation not in prefixes:
                    prefixes.insert(0, orientation)

    contexts = {
        text_id: {
            kind: " ".join(parts)
            for kind, parts in values.items()
            if parts
        }
        for text_id, values in sorted(raw_contexts.items())
    }
    stats = {
        "pages": page_count,
        "tables": table_count,
        "cells": cell_count,
        "inputs": input_count,
        "audio_context_ids": len(contexts),
    }
    return contexts, stats


def main() -> int:
    contexts, stats = build_contexts()
    OUTPUT_PATH.write_text(
        json.dumps(contexts, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(" ".join(f"{key}={value}" for key, value in stats.items()))
    print(f"output={OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
