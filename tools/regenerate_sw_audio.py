"""Regenerate ADT narration with a native Kiswahili neural voice.

The script caches speech by normalized text, so repeated text is synthesized once.
Each destination is replaced atomically only after a valid MP3 has been produced.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import json
import re
import shutil
import uuid
from pathlib import Path

import edge_tts


VOICE = "sw-TZ-RehemaNeural"
RATE = "-5%"


def spoken_text(value: str) -> str:
    value = html.unescape(value)
    replacements = (
        (r"\bhttps?\b", "echititipi"),
        (r"\bwww\b", "dabiliyu dabiliyu dabiliyu"),
        (r"\bs\s*\.\s*l\s*\.\s*p\s*\.?", "esielopi"),
        (r"\bUDOM\b", "yudomu"),
        (r"\bUDSM\b", "yudizimu"),
        (r"\bDUCE\b", "duse"),
        (r"\bTET\b", "TETI"),
        (r"\bMt\s*\.?", "mtakatifu"),
        (r"\bBi\s*\.?", "Bibi"),
        (r"\bBw\s*\.?", "Bwana"),
        (r"\bDr\s*\.?", "docta"),
        (r"\bProf\s*\.?", "profesa"),
        (r"\bVI\b", "sita"),
        (r"\bV\b", "tano"),
        (r"\bgo\b", "goo"),
        (r"\btz\b", "tizi"),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    value = value.replace("+", " julisha ")
    value = value.replace("/", " slashi ")
    value = re.sub(r"(?<!\w)\s*[-–—]\s*(?!\w)", " dashi ", value)
    value = re.sub(r"[._…]{3,}", ", ", value)
    value = re.sub(r"^[\s•*-]+", "", value, flags=re.MULTILINE)
    value = re.sub(r"\s*\n\s*", ". ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


async def synthesize(text: str, destination: Path, semaphore: asyncio.Semaphore) -> None:
    if destination.exists() and destination.stat().st_size > 1_000:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with semaphore:
        for attempt in range(1, 5):
            temporary = destination.with_name(
                f"{destination.stem}.{uuid.uuid4().hex}.part.mp3"
            )
            try:
                await asyncio.wait_for(
                    edge_tts.Communicate(text, VOICE, rate=RATE).save(str(temporary)),
                    timeout=45,
                )
                if temporary.stat().st_size <= 1_000:
                    raise RuntimeError("TTS returned an empty or invalid MP3")
                temporary.replace(destination)
                return
            except Exception:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
                if attempt == 4:
                    raise
                await asyncio.sleep(attempt * 2)


async def run(args: argparse.Namespace) -> None:
    repo = Path(__file__).resolve().parents[1]
    locale = repo / "content" / "i18n" / "sw-TZ"
    texts: dict[str, str] = json.loads((locale / "texts.json").read_text(encoding="utf-8"))
    audios: dict[str, str] = json.loads((locale / "audios.json").read_text(encoding="utf-8"))
    cache = Path(args.cache)
    selected_ids: set[str] | None = None
    if args.ids_file:
        selected_ids = {
            line.strip()
            for line in Path(args.ids_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        selected_ids |= {
            f"{data_id}_easy_read"
            for data_id in tuple(selected_ids)
            if not data_id.endswith("_easy_read")
        }

    jobs: dict[str, tuple[str, Path]] = {}
    destinations: dict[str, list[Path]] = {}
    for data_id, filename in audios.items():
        if args.prefix and not data_id.startswith(args.prefix):
            continue
        if selected_ids is not None and data_id not in selected_ids:
            continue
        normalized = spoken_text(texts[data_id])
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        jobs[digest] = (normalized, cache / f"{digest}.mp3")
        destinations.setdefault(digest, []).append(locale / "audio" / filename)

    ordered = sorted(jobs.items())
    if args.limit:
        ordered = ordered[: args.limit]
    selected = {digest for digest, _ in ordered}
    semaphore = asyncio.Semaphore(args.workers)
    completed = 0
    lock = asyncio.Lock()

    async def one(digest: str, job: tuple[str, Path]) -> None:
        nonlocal completed
        text, cached_file = job
        await synthesize(text, cached_file, semaphore)
        for target in destinations[digest]:
            temporary = target.with_suffix(".new.mp3")
            shutil.copyfile(cached_file, temporary)
            temporary.replace(target)
        async with lock:
            completed += 1
            if completed % 50 == 0 or completed == len(ordered):
                print(f"completed {completed}/{len(ordered)}", flush=True)

    await asyncio.gather(*(one(digest, job) for digest, job in ordered))
    files_written = sum(len(destinations[digest]) for digest in selected)
    print(f"Updated {files_written} audio files using {VOICE}.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache",
        default=r"C:\Users\Admin\Documents\New project\audio-sw-cache",
    )
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--ids-file", default="")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
