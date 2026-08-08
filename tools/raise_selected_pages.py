"""Move selected navigation-page content slightly upward."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "pg046_sec001.html",  # navigation 53
    "pg096_sec001.html",  # navigation 123
    "pg096_sec002.html",  # navigation 124
    "pg097_sec001.html",  # navigation 126
)


def main() -> None:
    for filename in FILES:
        path = ROOT / filename
        source = path.read_text(encoding="utf-8")
        pattern = r'(<div\b(?=[^>]*\bid="content")[^>]*)(>)'
        match = re.search(pattern, source)
        if not match:
            raise RuntimeError(f"Missing #content container in {filename}")
        opening = match.group(1)
        if "translateY(-2rem)" in opening:
            continue
        if re.search(r'\bstyle="', opening):
            opening = re.sub(
                r'style="([^"]*)"',
                lambda item: f'style="{item.group(1).rstrip(";")}; transform: translateY(-2rem);"',
                opening,
                count=1,
            )
        else:
            opening += ' style="transform: translateY(-2rem);"'
        updated = source[: match.start()] + opening + match.group(2) + source[match.end() :]
        path.write_text(updated, encoding="utf-8")
        print(f"Raised {filename}")


if __name__ == "__main__":
    main()
