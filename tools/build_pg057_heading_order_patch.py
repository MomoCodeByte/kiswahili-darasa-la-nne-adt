from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "pg057_sec001.html"
old = path.read_text(encoding="utf-8-sig")
new = old.replace('<h2 id="pg057-restored-heading"', '<h1 id="pg057-restored-heading"', 1)
new = new.replace('Zoezi la 6: Mazoezi ya lugha</h2>', 'Zoezi la 6: Mazoezi ya lugha</h1>', 1)
new = new.replace('<h1 class="text-4xl max-lg:text-4xl max-sm:text-[2.2rem] font-bold text-blue-700 leading-tight text-center max-sm:text-left" data-id="pg057_n0003">', '<h2 class="text-4xl max-lg:text-4xl max-sm:text-[2.2rem] font-bold text-blue-700 leading-tight text-center max-sm:text-left" data-id="pg057_n0003">', 1)
new = new.replace('Oanisha methali zinazofanana kutoka sehemu A na B.</h1>', 'Oanisha methali zinazofanana kutoka sehemu A na B.</h2>', 1)
new = new.replace('<h3 class="text-3xl max-sm:text-2xl font-bold text-blue-700">', '<h2 class="text-3xl max-sm:text-2xl font-bold text-blue-700">')
new = new.replace('</h3>', '</h2>')
if old == new:
    raise SystemExit("pg057 headings not found")
print("*** Begin Patch")
print(f"*** Update File: {path}")
print("@@")
for line in old.splitlines():
    if 'pg057-restored-heading' in line or 'data-id="pg057_n0003"' in line:
        print("-" + line)
for line in new.splitlines():
    if 'pg057-restored-heading' in line or 'data-id="pg057_n0003"' in line:
        print("+" + line)
print("*** End Patch")
