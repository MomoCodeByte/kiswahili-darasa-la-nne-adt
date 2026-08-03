from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}

target = root / "pg135_sec001.html"
old_target = target.read_text(encoding="utf-8-sig")
start = '<div role="group" aria-label="Mwendelezo wa zoezi E"'
if start not in old_target:
    start = '<section data-section-type="activity_fill_in_the_blank" data-section-id="pg135_sec001_e" aria-label="Mwendelezo wa zoezi E"'
start_at = old_target.index(start)
end_at = old_target.index('</div></div>', start_at) + len('</div></div>')
old_block = old_target[start_at:end_at]
new_block = '<section data-section-type="activity_fill_in_the_blank" data-section-id="pg135_sec001_e" aria-label="Mwendelezo wa zoezi E" class="max-w-4xl mx-auto rounded-2xl border border-stone-200 bg-stone-50 p-5 space-y-5 text-xl max-sm:text-lg"><p class="fitb-sentence" data-id="pg135_n0002">(iv) Taifa linataka [[blank:item-4]] wajiepushe na uharibifu wa miundombinu. (watu wote, baadhi ya watu, watu wengi, watu binafsi)</p><p class="fitb-sentence" data-id="pg135_n0003">(v) Asiyeuliza [[blank:item-5]] hana cha kujifunza. (maswali, hoja, majibu, habari)</p></section></div>'
new_target = old_target[:start_at] + new_block + old_target[end_at:]
changes[target] = (old_target, new_target, 'aria-label="Mwendelezo wa zoezi E"')

print("*** Begin Patch")
for path, (old, new, marker) in changes.items():
    print(f"*** Update File: {path}")
    print("@@")
    for line in old.splitlines():
        if marker in line:
            print("-" + line)
    for line in new.splitlines():
        if marker in line:
            print("+" + line)
print("*** End Patch")
