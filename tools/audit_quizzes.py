from __future__ import annotations

import html
import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
i18n = root / "content/i18n/sw-TZ"
texts = json.loads((i18n / "texts.json").read_text(encoding="utf-8-sig"))
audios = json.loads((i18n / "audios.json").read_text(encoding="utf-8-sig"))
issues: list[str] = []

for path in sorted(root.glob("qz*.html")):
    qz = path.stem
    source = path.read_text(encoding="utf-8-sig")
    attr_match = re.search(r"data-correct-answers='([^']+)'", source)
    script_match = re.search(r'id="quiz-correct-answers">([^<]+)</script>', source)
    window_match = re.search(r"window\.correctAnswers\s*=\s*JSON\.parse\('([^']+)'\)", source)
    if not (attr_match and script_match and window_match):
        issues.append(f"{qz}: missing correct-answer representation")
        continue
    attribute_answers = json.loads(html.unescape(attr_match.group(1)))
    script_answers = json.loads(html.unescape(script_match.group(1)))
    window_answers = json.loads(html.unescape(window_match.group(1)))
    if not (attribute_answers == script_answers == window_answers):
        issues.append(f"{qz}: correct-answer representations disagree")
    if sum(value is True for value in attribute_answers.values()) != 1:
        issues.append(f"{qz}: expected exactly one correct answer")
    option_ids = re.findall(r'data-activity-item="(' + re.escape(qz) + r'_o\d+)"', source)
    option_ids = list(dict.fromkeys(option_ids))
    if len(option_ids) != 3:
        issues.append(f"{qz}: expected 3 options, got {len(option_ids)}")
    required_ids = [f"{qz}_que"]
    for option_id in option_ids:
        required_ids.extend((option_id, f"{option_id}_exp"))
        if f'name="{qz}"' not in source:
            issues.append(f"{qz}: radio group name missing")
    for data_id in required_ids:
        if data_id not in texts:
            issues.append(f"{qz}: missing text {data_id}")
        filename = audios.get(data_id)
        if not filename or not (i18n / "audio" / filename).is_file():
            issues.append(f"{qz}: missing audio {data_id}")
    if 'role="activity"' not in source:
        issues.append(f"{qz}: role=activity missing")
    if 'role="group"' not in source or "aria-labelledby=" not in source:
        issues.append(f"{qz}: accessible option group missing")

print(json.dumps({"quizzes": len(list(root.glob('qz*.html'))), "issues": len(issues)}, indent=2))
for issue in issues:
    print(issue)
raise SystemExit(1 if issues else 0)
