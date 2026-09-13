from __future__ import annotations

import argparse
import io
import mimetypes
import posixpath
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REMOTE_BASE = "https://raw.githubusercontent.com/MomoCodeByte/kiswahili-darasa-la-nne-adt/main/"


class AdtHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_HEAD(self):
        if self._maybe_proxy_audio(send_body=False):
            return
        super().do_HEAD()

    def do_GET(self):
        if self._maybe_proxy_audio(send_body=True):
            return
        super().do_GET()

    def _maybe_proxy_audio(self, send_body: bool) -> bool:
        parsed = urllib.parse.urlparse(self.path)
        rel = urllib.parse.unquote(parsed.path.lstrip("/"))
        if not rel.startswith("content/i18n/") or "/audio/" not in rel or not rel.endswith(".mp3"):
            return False

        local_path = ROOT / Path(rel)
        if local_path.exists() and local_path.is_file() and local_path.stat().st_size > 0:
            return False

        remote_url = REMOTE_BASE + rel.replace("\\", "/")
        try:
            with urllib.request.urlopen(remote_url, timeout=120) as response:
                data = response.read() if send_body else b""
                content_type = response.headers.get_content_type() or "audio/mpeg"
                content_length = response.headers.get("Content-Length")
        except urllib.error.HTTPError as exc:
            self.send_error(exc.code, exc.reason)
            return True
        except OSError as exc:
            self.send_error(HTTPStatus.BAD_GATEWAY, f"Audio proxy failed: {exc}")
            return True

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        if content_length:
            self.send_header("Content-Length", content_length)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if send_body:
            self.wfile.write(data)
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), AdtHandler)
    print(f"Serving ADT book at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
