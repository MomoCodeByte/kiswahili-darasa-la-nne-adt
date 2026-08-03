from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXTS = json.loads((ROOT / "content/i18n/sw-TZ/texts.json").read_text(encoding="utf-8-sig"))


PAGE_IDS = {
    12: [
        "pg012_n0002", "pg012_n0003", "pg012_n0005", "pg012_n0006", "pg012_n0007",
        "pg012_n0010", "pg012_n0011", "pg012_n0013", "pg012_n0014", "pg012_n0016", "pg012_n0017",
        "pg012_n0019", "pg012_n0020", "pg012_n0022", "pg012_n0023", "pg012_n0025", "pg012_n0026",
        "pg012_n0032", "pg012_n0033", "pg012_n0035", "pg012_n0036", "pg012_n0039", "pg012_n0040",
        "pg012_n0042", "pg012_n0043", "pg012_n0045", "pg012_n0046", "pg012_n0048", "pg012_n0049",
        "pg012_n0051", "pg012_n0052", "pg012_n0054", "pg012_n0055", "pg012_n0057", "pg012_n0058",
        "pg012_n0059", "pg012_n0060", "pg012_n0061", "pg012_n0064", "pg012_n0065", "pg012_n0067",
        "pg012_n0068", "pg012_n0070", "pg012_n0071", "pg012_n0073", "pg012_n0074", "pg012_n0076",
        "pg012_n0077",
    ],
    21: [f"pg021_n{i:04d}" for i in range(1, 19)] + [f"pg021_n{i:04d}" for i in range(20, 28)],
    36: [f"pg036_n{i:04d}" for i in range(2, 12)] + [f"pg036_n{i:04d}" for i in range(13, 16)] + [f"pg036_n{i:04d}" for i in range(17, 32)],
}


def body_for(page: int) -> str:
    chunks: list[str] = []
    heading_ids = {
        12: {"pg012_n0002", "pg012_n0032", "pg012_n0054"},
        21: {"pg021_n0005", "pg021_n0020"},
        36: {"pg036_n0010"},
    }[page]
    instruction_ids = {
        12: {"pg012_n0003", "pg012_n0033", "pg012_n0055"},
        21: {"pg021_n0006", "pg021_n0021"},
        36: {"pg036_n0011"},
    }[page]
    for data_id in PAGE_IDS[page]:
        value = html.escape(str(TEXTS[data_id]))
        if data_id in heading_ids:
            chunks.append(f'<h2 class="section-letter" data-id="{data_id}">{value}</h2>')
        elif data_id in instruction_ids:
            chunks.append(f'<h3 class="instruction" data-id="{data_id}">{value}</h3>')
        elif "Mfano" in str(TEXTS[data_id]):
            chunks.append(f'<p class="example" data-id="{data_id}">{value}</p>')
        else:
            chunks.append(f'<p class="line" data-id="{data_id}">{value}</p>')
    return "\n        ".join(chunks)


def page_html(page: int) -> str:
    section_id = f"pg{page:03d}_sec001"
    return f'''<!DOCTYPE html>
<html lang="sw-TZ">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kiswahili: Kitabu cha Mwanafunzi Darasa la Nne</title>
  <meta name="title-id" content="{section_id}" />
  <meta name="page-section-id" content="0" />
  <link href="./content/tailwind_output.css" rel="stylesheet">
  <link href="./assets/libs/fontawesome/css/all.min.css" rel="stylesheet">
  <link href="./assets/fonts.css" rel="stylesheet">
  <style>
    body {{ margin:0; background:#fff; color:#111827; font-family:'Atkinson Hyperlegible','Merriweather',sans-serif; }}
    .restored-page {{ box-sizing:border-box; position:relative; width:min(100%,776px); min-height:100vh; margin:0 auto; padding:64px 76px 74px; overflow:hidden; }}
    .restored-page::before {{ content:'FOR ONLINE READING ONLY'; position:absolute; left:42px; top:54%; transform:rotate(-45deg); color:rgba(248,113,113,.38); font-size:42px; white-space:nowrap; pointer-events:none; }}
    .content-stack {{ position:relative; z-index:1; }}
    .section-letter {{ display:inline; margin:0 .7rem 0 0; color:#1d5fa7; font-size:20px; font-weight:800; }}
    .instruction {{ display:inline; margin:0; color:#1d5fa7; font-size:20px; line-height:1.35; font-weight:800; }}
    .example {{ margin:.75rem 0 .25rem 2.7rem; font-size:18px; font-weight:600; }}
    .line {{ margin:.35rem 0 .35rem 3.2rem; font-size:18px; line-height:1.35; }}
    @media (max-width:640px) {{ .restored-page {{ padding:36px 24px 64px; }} .section-letter,.instruction {{ font-size:18px; }} .line,.example {{ margin-left:1.25rem; font-size:16px; }} }}
  </style>
</head>
<body class="min-h-screen">
  <main>
    <h1 class="sr-only" id="page-heading">Ukurasa wa {page}</h1>
    <div id="content" class="opacity-0">
      <section role="article" aria-labelledby="page-heading" data-section-type="activity_open_ended_answer" data-section-id="{section_id}" class="restored-page">
        <div class="content-stack">
        {body_for(page)}
        </div>
      </section>
    </div>
  </main>
  <div class="relative z-50" id="interface-container"></div>
  <div class="relative z-50" id="nav-container"></div>
  <script src="./assets/offline-preloader.js"></script>
  <script src="./assets/scorm.js"></script>
  <script src="./assets/base.bundle.local.js"></script>
</body>
</html>
'''


def page20_html() -> str:
    section_id = "pg020_sec001"
    b_ids = [
        "pg020_n0003", "pg020_n0004", "pg020_n0007", "pg020_n0008", "pg020_n0010", "pg020_n0011",
        "pg020_n0013", "pg020_n0014", "pg020_n0016", "pg020_n0017", "pg020_n0019", "pg020_n0020",
        "pg020_n0022", "pg020_n0023",
    ]
    b_lines = "\n".join(
        f'<p class="line" data-id="{data_id}">{html.escape(str(TEXTS[data_id]))}</p>' for data_id in b_ids
    )
    return f'''<!DOCTYPE html>
<html lang="sw-TZ">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kiswahili: Kitabu cha Mwanafunzi Darasa la Nne</title>
  <meta name="title-id" content="{section_id}" />
  <meta name="page-section-id" content="0" />
  <link href="./content/tailwind_output.css" rel="stylesheet">
  <link href="./assets/libs/fontawesome/css/all.min.css" rel="stylesheet">
  <link href="./assets/fonts.css" rel="stylesheet">
  <style>
    body{{margin:0;background:#fff;color:#111827;font-family:'Atkinson Hyperlegible','Merriweather',sans-serif}}
    .page{{box-sizing:border-box;position:relative;width:min(100%,776px);min-height:100vh;margin:auto;padding:62px 76px 76px;overflow:hidden}}
    .page::before{{content:'FOR ONLINE READING ONLY';position:absolute;left:38px;top:55%;transform:rotate(-45deg);color:rgba(248,113,113,.38);font-size:42px;white-space:nowrap}}
    .stack{{position:relative;z-index:1}} .heading{{color:#1d5fa7;font-size:20px;font-weight:800;margin:10px 0 6px}}
    .line{{font-size:18px;line-height:1.3;margin:5px 0 5px 42px}} .example{{font-size:18px;margin:7px 0 7px 42px}}
    @media(max-width:640px){{.page{{padding:34px 24px 64px}}.heading{{font-size:18px}}.line,.example{{font-size:16px;margin-left:18px}}}}
  </style>
</head>
<body><main><h1 id="page-heading" class="sr-only">Mazoezi ya lugha</h1><div id="content" class="opacity-0">
  <section role="article" aria-labelledby="page-heading" data-section-type="activity_open_ended_answer" data-section-id="{section_id}" class="page"><div class="stack">
    <h2 class="heading"><span data-id="pg020_n0003">{html.escape(TEXTS['pg020_n0003'])}</span> <span data-id="pg020_n0004">{html.escape(TEXTS['pg020_n0004'])}</span></h2>
    {b_lines}
    <h2 class="heading"><span data-id="pg020_n0030">{html.escape(TEXTS['pg020_n0030'])}</span> <span data-id="pg020_n0031">{html.escape(TEXTS['pg020_n0031'])}</span></h2>
    <p class="example"><strong>Mfano:</strong> cheka - <em>nuna</em><br>ng'oa - <em>panda</em></p>
    <p class="line">(i) masika ___________</p><p class="line">(ii) zamani ___________</p>
    <p class="line">(iii) bondeni ___________</p><p class="line">(iv) furaha ___________</p>
    <p class="line">(v) mbali ___________</p><p class="line">(vi) faida ___________</p>
    <p class="line">(vii) achia ___________</p><p class="line">(viii) toka ___________</p>
    <h2 class="heading"><span data-id="pg020_n0060">{html.escape(TEXTS['pg020_n0060'])}</span> <span data-id="pg020_n0061">{html.escape(TEXTS['pg020_n0061'])}</span></h2>
    <p class="example"><strong>Mfano:</strong> Mtoto wanacheza mpira.<br><em>Mtoto anacheza mpira.</em><br><em>Watoto wanacheza mpira.</em></p>
    <p class="line">(i) Mwalimu Mbilo waliwaambia wanafunzi warudi nyumbani.</p>
  </div></section>
  </div></main><div id="interface-container"></div><div id="nav-container"></div>
  <script src="./assets/offline-preloader.js"></script><script src="./assets/scorm.js"></script><script src="./assets/base.bundle.local.js"></script>
</body></html>
'''


def add_file_patch(path: Path, contents: str) -> str:
    lines = "\n".join("+" + line for line in contents.splitlines())
    return f"*** Add File: {path}\n{lines}\n"


print("*** Begin Patch")
print(add_file_patch(ROOT / "pg020_sec001.html", page20_html()), end="")
print("*** End Patch")
