from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "texts.json"
AUDIOS_PATH = ROOT / "content" / "i18n" / "sw-TZ" / "audios.json"
PAGES_PATH = ROOT / "content" / "pages.json"
AUDIO_DIR = ROOT / "content" / "i18n" / "sw-TZ" / "audio"
MANIFEST_PATH = ROOT / "assets" / "reading-audio-manifest-v2.js"
TABLE_AUDIO_CONTEXTS_PATH = ROOT / "assets" / "table-audio-contexts.json"

LETTER_WORDS = {
    "a": "aa",
    "b": "bee",
    "c": "chee",
    "d": "dee",
    "e": "ee",
    "f": "efu",
    "g": "gee",
    "h": "hee",
}

ROMAN_PREFIX_RE = re.compile(r"^\s*\(([ivxlcdm]+)\)(?=\s|$)\s*", re.IGNORECASE)
ROMAN_DOT_PREFIX_RE = re.compile(r"^\s*([ivxlcdm]+)\.\s*", re.IGNORECASE)
PAREN_LETTER_PREFIX_RE = re.compile(r"^\s*\(([a-h])\)(?=\s|$)\s*", re.IGNORECASE)
LETTER_PREFIX_RE = re.compile(r"^\s*([a-h])\.\s*", re.IGNORECASE)
KIFUNGU_LETTER_RE = re.compile(r"\b(Kifungu)\s+([a-h])\b", re.IGNORECASE)
BLANK_RE = re.compile(r"\[\[blank:item-\d+(?::[^\]]+)?\]\]", re.IGNORECASE)
ELLIPSIS_RE = re.compile(r"(?:(?:\u2026)+|(?:\.{2,}))+", re.IGNORECASE)
TIMES_TWO_RE = re.compile(r"\bx\s*2\b", re.IGNORECASE)
ONE_TO_EIGHT_RE = re.compile(r"\b1\s*[-\u2013]\s*8\b")

ELLIPSIS_DASH_IDS = {
    "pg088_n0015",
    "pg088_n0018",
    "pg088_n0021",
    "pg088_n0022",
    "pg088_n0023",
    "pg088_n0024",
    "pg088_n0025",
    "pg088_n0026",
    "pg088_n0027",
}
INPUT_DASH_IDS = {
    "pg105_n0064",
    "pg105_n0065",
    "pg105_n0072",
    "pg105_n0073",
    "pg106_n0008",
    "pg106_n0009",
}
SAMPLE_SEPARATOR_IDS = {
    "pg108_n0074",
    "pg108_n0075",
    "pg109_n0004",
    "pg109_n0005",
}
SUPPLEMENT_CONTENT_IDS = {
    "pg097_n0056",
    "pg097_n0057",
    "pg097_n0058",
    "pg097_n0059",
}

# Page 12 relies on two visual tables. These recordings expose the table
# structure without changing or duplicating any visible book content.
PAGE_12_ACCESSIBLE_AUDIO = {
    "pg011_n0002": "Sehemu bee.",
    "pg011_n0003": (
        "Tunga sentensi kumi kwa kutumia jedwali lifuatalo. Jedwali lina safu "
        "tatu na mistari mitano. Chagua kipande cha mwanzo kutoka safu ya kwanza, "
        "neno la kulinganisha kutoka safu ya pili, na kipande cha mwisho kutoka "
        "safu ya tatu ili kutunga sentensi yenye maana."
    ),
    "pg011_n0004": "Mifano ya sentensi kamili ni hii.",
    "pg011_n0006": "Mfano wa kwanza. Bahati ni mrefu kuliko wazazi wake.",
    "pg011_n0007": (
        "Mfano wa pili. Chaupole alimaliza kulima mapema zaidi ya watu wote."
    ),
    "pg011_n0011": "Mstari wa kwanza, safu ya kwanza. Bahati ni mrefu.",
    "pg011_n0013": "Mstari wa kwanza, safu ya pili. kuliko.",
    "pg011_n0015": "Mstari wa kwanza, safu ya tatu. vijana wenzake.",
    "pg011_n0018": "Mstari wa pili, safu ya kwanza. Maganga ni mfupi.",
    "pg011_n0020": "Mstari wa pili, safu ya pili. zaidi ya.",
    "pg011_n0022": "Mstari wa pili, safu ya tatu. wazazi wake.",
    "pg011_n0025": (
        "Mstari wa tatu, safu ya kwanza. Chaupole alimaliza kulima mapema."
    ),
    "pg011_n0027": "Mstari wa tatu, safu ya pili. kama.",
    "pg011_n0029": "Mstari wa tatu, safu ya tatu. watu wote.",
    "pg011_n0032": (
        "Mstari wa nne, safu ya kwanza. Chausiku hakumaliza zoezi."
    ),
    "pg011_n0034": "Mstari wa nne, safu ya pili. mithili ya.",
    "pg011_n0036": "Mstari wa nne, safu ya tatu. wanafunzi wenzake.",
    "pg011_n0039": "Mstari wa tano, safu ya kwanza. Chipola hana juhudi.",
    "pg011_n0041": "Mstari wa tano, safu ya pili. mfano wa.",
    "pg011_n0044": "Sehemu chee.",
    "pg011_n0045": (
        "Andika umoja au wingi wa maneno yafuatayo. Jedwali lina safu mbili. "
        "Safu ya umoja ipo kushoto, na safu ya wingi ipo kulia. Kwa kila swali, "
        "neno moja limetolewa na nafasi ya jibu ipo upande mwingine. Tambua kama "
        "neno lililotolewa ni umoja au wingi, kisha andika umbo linalokosekana. "
        "Namba za maswali zitasomwa kuanzia moja hadi kumi."
    ),
    "pg011_n0050": "Kichwa cha safu ya kwanza. Umoja.",
    "pg011_n0052": "Kichwa cha safu ya pili. Wingi.",
    "pg011_n0055": "Mfano wa umoja na wingi.",
    "pg011_n0057": "Umoja. mtoto.",
    "pg011_n0059": "Wingi. watoto.",
    "pg011_n0063": "Umoja. chungwa.",
    "pg011_n0065": "Wingi. machungwa.",
    "pg011_n0068": "Swali la kwanza. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0070": "Neno la umoja. kijiji.",
    "pg011_n0075": "Swali la pili. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0077": "Neno la umoja. eneo.",
    "pg011_n0082": "Swali la tatu. Wingi umetolewa. Andika umoja kwenye nafasi ya jibu.",
    "pg011_n0086": "Neno la wingi. miaka.",
    "pg011_n0089": "Swali la nne. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0091": "Neno la umoja. ardhi.",
    "pg011_n0096": "Swali la tano. Wingi umetolewa. Andika umoja kwenye nafasi ya jibu.",
    "pg011_n0100": "Neno la wingi. nyaya.",
    "pg011_n0103": "Swali la sita. Wingi umetolewa. Andika umoja kwenye nafasi ya jibu.",
    "pg011_n0107": "Neno la wingi. vikao.",
    "pg011_n0110": "Swali la saba. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0112": "Neno la umoja. jukumu.",
    "pg011_n0117": "Swali la nane. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0119": "Neno la umoja. zao.",
    "pg011_n0124": "Swali la tisa. Wingi umetolewa. Andika umoja kwenye nafasi ya jibu.",
    "pg011_n0128": "Neno la wingi. mahafali.",
    "pg011_n0131": "Swali la kumi. Umoja umetolewa. Andika wingi kwenye nafasi ya jibu.",
    "pg011_n0133": "Neno la umoja. mhitimu.",
}


@dataclass(frozen=True)
class Candidate:
    text_id: str
    page_id: str
    audio_filename: str
    original: str
    spoken: str
    changes: tuple[str, ...]


def int_to_roman(number: int) -> str:
    values = (
        (1000, "m"),
        (900, "cm"),
        (500, "d"),
        (400, "cd"),
        (100, "c"),
        (90, "xc"),
        (50, "l"),
        (40, "xl"),
        (10, "x"),
        (9, "ix"),
        (5, "v"),
        (4, "iv"),
        (1, "i"),
    )
    result: list[str] = []
    for value, numeral in values:
        while number >= value:
            result.append(numeral)
            number -= value
    return "".join(result)


def roman_to_int(numeral: str) -> int | None:
    values = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    token = numeral.lower()
    total = 0
    previous = 0
    for char in reversed(token):
        value = values[char]
        total += -value if value < previous else value
        previous = max(previous, value)
    if total < 1 or total > 3999 or int_to_roman(total) != token:
        return None
    return total


def swahili_number(number: int) -> str:
    ones = {
        1: "moja",
        2: "mbili",
        3: "tatu",
        4: "nne",
        5: "tano",
        6: "sita",
        7: "saba",
        8: "nane",
        9: "tisa",
        10: "kumi",
    }
    tens = {
        20: "ishirini",
        30: "thelathini",
        40: "arobaini",
        50: "hamsini",
        60: "sitini",
        70: "sabini",
        80: "themanini",
        90: "tisini",
    }
    if number in ones:
        return ones[number]
    if 10 < number < 20:
        return f"kumi na {ones[number - 10]}"
    if 20 <= number < 100:
        base = number - (number % 10)
        remainder = number % 10
        return tens[base] if remainder == 0 else f"{tens[base]} na {ones[remainder]}"
    raise ValueError(f"Roman numeral {number} is outside the supported reading range 1-99")


def base_text_id(text_id: str | None) -> str | None:
    if text_id is None:
        return None
    return re.sub(r"_easy_read$", "", text_id)


@lru_cache(maxsize=1)
def load_table_audio_contexts() -> dict[str, dict[str, str]]:
    if not TABLE_AUDIO_CONTEXTS_PATH.exists():
        return {}
    payload = read_json(TABLE_AUDIO_CONTEXTS_PATH)
    contexts: dict[str, dict[str, str]] = {}
    for text_id, context in payload.items():
        if not isinstance(context, dict):
            raise ValueError(f"Invalid table audio context for {text_id}")
        prefix = context.get("prefix", "")
        suffix = context.get("suffix", "")
        if not isinstance(prefix, str) or not isinstance(suffix, str):
            raise ValueError(f"Invalid table audio context strings for {text_id}")
        contexts[text_id] = {"prefix": prefix.strip(), "suffix": suffix.strip()}
    return contexts


def rewrite_for_reading(
    value: str, text_id: str | None = None
) -> tuple[str, tuple[str, ...]]:
    spoken = re.sub(r"\s+", " ", value).strip()
    changes: list[str] = []
    source_id = base_text_id(text_id)

    accessible_audio = PAGE_12_ACCESSIBLE_AUDIO.get(source_id)
    if accessible_audio is not None:
        return accessible_audio, ("accessible_context",)

    prefix_was_rewritten = False
    roman_match = ROMAN_PREFIX_RE.match(spoken) or ROMAN_DOT_PREFIX_RE.match(spoken)
    if roman_match:
        number = roman_to_int(roman_match.group(1))
        if number is not None and number <= 99:
            label = swahili_number(number)
            rest = spoken[roman_match.end() :].strip()
            spoken = label if not rest else f"{label}. {rest}"
            changes.append("roman")
            prefix_was_rewritten = True

    if not prefix_was_rewritten:
        parenthesized_letter_match = PAREN_LETTER_PREFIX_RE.match(spoken)
        if parenthesized_letter_match:
            label = LETTER_WORDS[parenthesized_letter_match.group(1).lower()]
            rest = spoken[parenthesized_letter_match.end() :].strip()
            spoken = label if not rest else f"{label}. {rest}"
            changes.append("letter")
            prefix_was_rewritten = True

    if not prefix_was_rewritten:
        letter_match = LETTER_PREFIX_RE.match(spoken)
        if letter_match:
            label = LETTER_WORDS[letter_match.group(1).lower()]
            rest = spoken[letter_match.end() :].strip()
            spoken = label if not rest else f"{label}. {rest}"
            changes.append("letter")

    def replace_kifungu(match: re.Match[str]) -> str:
        letter = match.group(2).lower()
        return f"{match.group(1)} {LETTER_WORDS[letter]}"

    rewritten_kifungu = KIFUNGU_LETTER_RE.sub(replace_kifungu, spoken)
    if rewritten_kifungu != spoken:
        spoken = rewritten_kifungu
        changes.append("kifungu")

    rewritten_blanks = BLANK_RE.sub("dash", spoken)
    if rewritten_blanks != spoken:
        spoken = rewritten_blanks
        changes.append("blank")

    if source_id in ELLIPSIS_DASH_IDS:
        rewritten_ellipsis = ELLIPSIS_RE.sub(" dash ", spoken)
        if rewritten_ellipsis != spoken:
            spoken = rewritten_ellipsis
            changes.append("ellipsis_blank")

    if source_id in INPUT_DASH_IDS and not re.search(r"\bdash\b", spoken, re.IGNORECASE):
        spoken = f"{spoken}. dash"
        changes.append("input_blank")

    if source_id in SAMPLE_SEPARATOR_IDS:
        rewritten_separator = re.sub(r"\s+[\u2013-]\s+", ", dash, ", spoken)
        if rewritten_separator != spoken:
            spoken = rewritten_separator
            changes.append("separator")

    rewritten_repeat = TIMES_TWO_RE.sub("mara mbili", spoken)
    if rewritten_repeat != spoken:
        spoken = rewritten_repeat
        changes.append("repeat")

    rewritten_range = ONE_TO_EIGHT_RE.sub("moja hadi nane", spoken)
    if rewritten_range != spoken:
        spoken = rewritten_range
        changes.append("range")

    if source_id in SUPPLEMENT_CONTENT_IDS:
        changes.append("supplement")

    table_context = load_table_audio_contexts().get(source_id or "")
    if table_context:
        prefix = table_context.get("prefix", "")
        suffix = table_context.get("suffix", "")
        if prefix:
            spoken = f"{prefix} {spoken}"
        if suffix:
            spoken = f"{spoken} {suffix}"
        changes.append("table_context")

    spoken = re.sub(r"\s+([,.])", r"\1", spoken)
    spoken = re.sub(r"\s{2,}", " ", spoken).strip()
    return spoken, tuple(changes)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def reader_page_to_id(reader_page: int) -> str:
    with PAGES_PATH.open("r", encoding="utf-8") as handle:
        pages = json.load(handle)
    for page in pages:
        if page.get("page_number") == reader_page:
            section_id = str(page.get("section_id", ""))
            match = re.match(r"^(pg\d+)", section_id)
            if match:
                return match.group(1)
    raise ValueError(f"Reader page {reader_page} was not found in {PAGES_PATH}")


def collect_candidates(
    page_ids: set[str] | None = None,
    text_ids: set[str] | None = None,
    force_all_text: bool = False,
) -> tuple[list[Candidate], list[str]]:
    texts = read_json(TEXTS_PATH)
    audios = read_json(AUDIOS_PATH)
    candidates: list[Candidate] = []
    missing_audio: list[str] = []
    audio_owner: dict[str, str] = {}

    for text_id, original in texts.items():
        if not isinstance(original, str):
            continue
        if not original.strip():
            continue
        page_match = re.match(r"^((?:pg|qz)\d+)", text_id)
        page_id = page_match.group(1) if page_match else "other"
        if page_ids is not None and page_id not in page_ids:
            continue
        if text_ids is not None and text_id not in text_ids:
            continue
        spoken, changes = rewrite_for_reading(original, text_id)
        if force_all_text:
            changes = (*changes, "full_page")
        if not changes or (
            spoken == original
            and not {"supplement", "full_page"}.intersection(changes)
        ):
            continue
        filename = audios.get(text_id)
        if not isinstance(filename, str):
            missing_audio.append(text_id)
            continue
        if Path(filename).name != filename or not filename.lower().endswith(".mp3"):
            raise ValueError(f"Unsafe or unsupported audio filename for {text_id}: {filename}")
        previous_owner = audio_owner.get(filename)
        if previous_owner is not None and previous_owner != text_id:
            raise ValueError(
                f"Audio filename {filename} is shared by {previous_owner} and {text_id}"
            )
        audio_owner[filename] = text_id
        candidates.append(
            Candidate(
                text_id=text_id,
                page_id=page_id,
                audio_filename=filename,
                original=original,
                spoken=spoken,
                changes=changes,
            )
        )
    candidates.sort(key=lambda item: item.text_id)
    return candidates, sorted(missing_audio)


def resolve_section_files(
    section_files: list[str] | None, section_list: Path | None
) -> list[Path]:
    values = list(section_files or [])
    if section_list is not None:
        list_path = section_list if section_list.is_absolute() else ROOT / section_list
        values.extend(
            line.strip()
            for line in list_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    resolved: list[Path] = []
    for value in values:
        path = Path(value)
        path = path if path.is_absolute() else ROOT / path
        path = path.resolve()
        if not path.is_file() or path.suffix.lower() != ".html":
            raise ValueError(f"Section file was not found or is not HTML: {path}")
        resolved.append(path)
    return resolved


def collect_section_text_ids(paths: list[Path]) -> set[str]:
    text_ids: set[str] = set()
    for path in paths:
        source = path.read_text(encoding="utf-8")
        for text_id in re.findall(r'\bdata-id=["\']([^"\']+)["\']', source):
            text_ids.add(text_id)
            text_ids.add(f"{text_id}_easy_read")
    return text_ids


def load_manifest_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    source = path.read_text(encoding="utf-8")
    match = re.search(r"=\s*(\[[\s\S]*?\])\s*;", source)
    if not match:
        raise ValueError(f"Could not parse corrected audio manifest: {path}")
    payload = json.loads(match.group(1))
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError(f"Invalid corrected audio manifest: {path}")
    return set(payload)


def write_manifest(path: Path, text_ids: set[str], low_space: bool = False) -> None:
    payload = json.dumps(sorted(text_ids), indent=2, ensure_ascii=True)
    content = (
        "// Generated by tools/generate_kiswahili_reading_audio.py\n"
        f"window.__ADT_CORRECTED_RECORDED_AUDIO_IDS__ = {payload};\n"
    )
    if low_space:
        path.write_text(content, encoding="utf-8", newline="\n")
    else:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, path)


async def generate_audio(
    candidates: list[Candidate], voice: str, rate: str, jobs: int, low_space: bool
) -> tuple[list[Candidate], list[tuple[Candidate, str]]]:
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError(
            "edge-tts is required. Install it with: python -m pip install edge-tts"
        ) from exc

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(jobs)
    completed = 0
    lock = asyncio.Lock()
    successful: list[Candidate] = []
    failed: list[tuple[Candidate, str]] = []

    async def generate_one(candidate: Candidate) -> None:
        nonlocal completed
        output = AUDIO_DIR / candidate.audio_filename
        temporary = output if low_space else output.with_suffix(output.suffix + ".tmp")
        error: str | None = None
        try:
            async with semaphore:
                try:
                    for attempt in range(1, 4):
                        try:
                            communicate = edge_tts.Communicate(
                                candidate.spoken, voice=voice, rate=rate
                            )
                            await communicate.save(str(temporary))
                            break
                        except Exception:
                            if attempt == 3:
                                raise
                    if temporary.stat().st_size < 1000:
                        raise RuntimeError(
                            f"Generated audio is unexpectedly small: {temporary}"
                        )
                    if not low_space:
                        os.replace(temporary, output)
                finally:
                    if not low_space:
                        temporary.unlink(missing_ok=True)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        async with lock:
            completed += 1
            if error is None:
                successful.append(candidate)
            else:
                failed.append((candidate, error))
            if completed % 25 == 0 or completed == len(candidates):
                print(f"Generated {completed}/{len(candidates)} audio files")

    await asyncio.gather(*(generate_one(candidate) for candidate in candidates))
    return successful, failed


def write_report(
    path: Path, candidates: list[Candidate], missing_audio: list[str]
) -> None:
    base_count = sum(not item.text_id.endswith("_easy_read") for item in candidates)
    report = {
        "candidate_count": len(candidates),
        "base_candidate_count": base_count,
        "easy_read_candidate_count": len(candidates) - base_count,
        "page_count": len({item.page_id for item in candidates}),
        "change_counts": dict(
            sorted(Counter(change for item in candidates for change in item.changes).items())
        ),
        "missing_audio_mapping": missing_audio,
        "candidates": [asdict(item) for item in candidates],
    }
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def print_summary(candidates: list[Candidate], missing_audio: list[str]) -> None:
    counts = Counter(change for item in candidates for change in item.changes)
    base_count = sum(not item.text_id.endswith("_easy_read") for item in candidates)
    print(f"Candidates: {len(candidates)}")
    print(f"Base: {base_count}; Easy Read: {len(candidates) - base_count}")
    print(f"Pages: {len({item.page_id for item in candidates})}")
    print("Changes: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print(f"Missing audio mappings: {len(missing_audio)}")
    print("\nSample:")
    for item in candidates[:20]:
        print(f"  {item.text_id}: {item.original!r} -> {item.spoken!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate corrected Kiswahili audio for Roman numerals and letter labels."
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--page-id", action="append", help="Page key such as pg062")
    scope.add_argument("--reader-page", type=int, help="Reader page number such as 72")
    scope.add_argument(
        "--section-file", action="append", help="Exact HTML section file; may be repeated"
    )
    scope.add_argument(
        "--section-list", type=Path, help="Text file containing one HTML section per line"
    )
    scope.add_argument("--all", action="store_true", help="Apply to every matching page")
    parser.add_argument("--apply", action="store_true", help="Generate MP3 files and update manifest")
    parser.add_argument("--voice", default="sw-TZ-RehemaNeural")
    parser.add_argument("--rate", default="-5%")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument(
        "--force-all-text",
        action="store_true",
        help="Record every mapped text in the selected scope, including unchanged text",
    )
    parser.add_argument(
        "--low-space",
        action="store_true",
        help="Overwrite audio and manifest files directly instead of using temporary files",
    )
    parser.add_argument(
        "--only-missing-manifest",
        action="store_true",
        help="Generate only corrected audio IDs not already recorded in the manifest",
    )
    parser.add_argument(
        "--change",
        action="append",
        help="Generate only candidates containing this change type; may be repeated",
    )
    parser.add_argument("--report", type=Path, help="Write a JSON dry-run/apply report")
    args = parser.parse_args()
    if args.apply and not (
        args.all or args.page_id or args.reader_page or args.section_file or args.section_list
    ):
        parser.error(
            "--apply requires --page-id, --reader-page, --section-file, --section-list, or --all"
        )
    if args.jobs < 1 or args.jobs > 12:
        parser.error("--jobs must be between 1 and 12")
    return args


def main() -> int:
    args = parse_args()
    page_ids: set[str] | None = None
    text_ids: set[str] | None = None
    if args.page_id:
        page_ids = set(args.page_id)
    elif args.reader_page is not None:
        page_ids = {reader_page_to_id(args.reader_page)}
        print(f"Reader page {args.reader_page} maps to {next(iter(page_ids))}")
    elif args.section_file or args.section_list:
        section_files = resolve_section_files(args.section_file, args.section_list)
        text_ids = collect_section_text_ids(section_files)
        print(f"Sections: {len(section_files)}; text IDs in scope: {len(text_ids)}")

    candidates, missing_audio = collect_candidates(page_ids, text_ids, args.force_all_text)
    if args.change:
        requested_changes = set(args.change)
        candidates = [
            candidate
            for candidate in candidates
            if requested_changes.intersection(candidate.changes)
        ]
    if args.only_missing_manifest:
        manifest_ids = load_manifest_ids(MANIFEST_PATH)
        candidates = [
            candidate for candidate in candidates if candidate.text_id not in manifest_ids
        ]
    print_summary(candidates, missing_audio)
    if args.report:
        report_path = args.report if args.report.is_absolute() else ROOT / args.report
        write_report(report_path, candidates, missing_audio)
        print(f"Report: {report_path}")

    if not args.apply:
        print("\nDry run only. Add --apply with an explicit page scope or --all to generate audio.")
        return 0
    if not candidates:
        print("No matching audio files need generation.")
        return 0

    successful, failed = asyncio.run(
        generate_audio(candidates, args.voice, args.rate, args.jobs, args.low_space)
    )
    manifest_ids = load_manifest_ids(MANIFEST_PATH)
    manifest_ids.update(candidate.text_id for candidate in successful)
    manifest_ids.difference_update(candidate.text_id for candidate, _ in failed)
    write_manifest(MANIFEST_PATH, manifest_ids, args.low_space)
    print(f"Manifest entries: {len(manifest_ids)}")
    if failed:
        print(f"Failed audio files: {len(failed)}")
        for candidate, error in failed[:20]:
            print(f"  {candidate.text_id}: {error}")
        if len(failed) > 20:
            print(f"  ... and {len(failed) - 20} more")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
