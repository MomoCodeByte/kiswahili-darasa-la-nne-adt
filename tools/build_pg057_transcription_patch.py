from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "pg057_sec001.html"
old = path.read_text(encoding="utf-8-sig")
new = old.replace(
    '<div class="sr-only" data-pdf-transcription="pg057" aria-label="Maandishi yaliyomo kwenye picha ya ukurasa huu">',
    '<div class="hidden" aria-hidden="true" data-pdf-transcription="pg057">',
    1,
)
if old == new:
    raise SystemExit("pg057 transcription marker not found")
print("*** Begin Patch")
print(f"*** Update File: {path}")
print("@@")
for line in old.splitlines():
    if 'data-pdf-transcription="pg057"' in line:
        print("-" + line)
for line in new.splitlines():
    if 'data-pdf-transcription="pg057"' in line:
        print("+" + line)
print("*** End Patch")
