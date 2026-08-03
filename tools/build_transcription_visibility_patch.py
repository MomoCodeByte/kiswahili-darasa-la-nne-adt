from pathlib import Path

root = Path(__file__).resolve().parents[1]
targets = {
    "pg069_sec001.html": (
        '<div class="sr-only" data-pdf-transcription="pg069" aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">',
        '<div class="hidden" aria-hidden="true" data-pdf-transcription="pg069">',
    ),
    "pg110_sec001.html": (
        '<div class="sr-only" data-pdf-transcription="pg110" aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">',
        '<div class="hidden" aria-hidden="true" data-pdf-transcription="pg110">',
    ),
    "pg117_sec001.html": (
        '<div class="sr-only" data-pdf-transcription="pg117" aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">',
        '<div class="hidden" aria-hidden="true" data-pdf-transcription="pg117">',
    ),
    "pg100_sec001.html": (
        '<div class="sr-only" data-pdf-transcription="pg100" aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">',
        '<div class="hidden" aria-hidden="true" data-pdf-transcription="pg100">',
    ),
}
print("*** Begin Patch")
for filename, (needle, replacement) in targets.items():
    path = root / filename
    old = path.read_text(encoding="utf-8-sig")
    new = old.replace(needle, replacement, 1)
    if old == new:
        if replacement in old:
            continue
        raise SystemExit(f"marker not found: {filename}")
    print(f"*** Update File: {path}")
    print("@@")
    for line in old.splitlines():
        if needle in line:
            print("-" + line)
    for line in new.splitlines():
        if replacement in line:
            print("+" + line)
print("*** End Patch")
