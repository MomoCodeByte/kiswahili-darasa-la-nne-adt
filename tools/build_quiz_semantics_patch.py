from pathlib import Path


root = Path(__file__).resolve().parents[1]
print("*** Begin Patch")
for path in sorted(root.glob("qz*.html")):
    source = path.read_text(encoding="utf-8-sig")
    old = "    <section\n        id=\"simple-main\""
    new = "    <section\n        role=\"activity\"\n        id=\"simple-main\""
    if 'role="activity"' in source:
        continue
    if old not in source:
        raise RuntimeError(f"Quiz section pattern missing: {path.name}")
    print(f"*** Update File: {path}")
    print("@@")
    print("-    <section")
    print("-        id=\"simple-main\"")
    print("+    <section")
    print("+        role=\"activity\"")
    print("+        id=\"simple-main\"")
print("*** End Patch")
