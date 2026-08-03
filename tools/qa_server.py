from __future__ import annotations

import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]


class QAHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = unquote(urlparse(path).path).lstrip("/")
        return str((ROOT / clean).resolve())

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        requested = ROOT / unquote(parsed.path).lstrip("/")
        if requested.suffix.lower() == ".html" and requested.is_file():
            html = requested.read_text(encoding="utf-8-sig")
            html = re.sub(r"<script\b[^>]*\bsrc=[^>]*>\s*</script>", "", html, flags=re.I)
            html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.I | re.S)
            html = html.replace("opacity-0", "opacity-100")
            html = html.replace("</head>", "<style>#interface-container,#nav-container{display:none!important}</style></head>")
            payload = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8766), QAHandler)
    print("ADT QA server: http://127.0.0.1:8766", flush=True)
    server.serve_forever()
