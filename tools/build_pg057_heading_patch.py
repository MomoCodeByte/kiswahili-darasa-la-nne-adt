from pathlib import Path


root = Path(__file__).resolve().parents[1]
path = root / "pg057_sec001.html"
source = path.read_text(encoding="utf-8-sig")
old = '<h1 class="text-4xl max-lg:text-4xl max-sm:text-[2rem] font-bold text-blue-700 leading-tight" data-id="pg057_n0010">Andika sentensi zifuatazo kwa ukanushi.</h1>'
new = '<h2 class="text-4xl max-lg:text-4xl max-sm:text-[2rem] font-bold text-blue-700 leading-tight" data-id="pg057_n0010">Andika sentensi zifuatazo kwa ukanushi.</h2>'
if old not in source:
    raise RuntimeError("Expected second h1 not found")
updated = source.replace(old, new, 1)
old_line = next(line for line in source.splitlines() if old in line)
new_line = next(line for line in updated.splitlines() if new in line)
print("*** Begin Patch")
print(f"*** Update File: {path}")
print("@@")
print("-" + old_line)
print("+" + new_line)
print("*** End Patch")
