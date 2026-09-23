"""Yes or No — ask Jev (TypeSafe's System-One model) a yes/no question.

    export TYPESAFE_API_KEY=...
    python server.py            # http://localhost:8765

Stdlib only. Serves index.html and proxies POST /ask to api.typesafe.ai so the
key never reaches the browser.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
TYPESAFE_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = os.environ.get("JEV_MODEL", "jev-latest")
PORT = int(os.environ.get("PORT", "8765"))

INSTRUCTIONS = (
    "`question` is a yes/no question. Answer it truthfully to the best of your "
    "knowledge. True means the honest answer is YES; false means the honest answer is NO."
)


def ask_jev(question: str) -> dict:
    api_key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("Jev")
    if not api_key:
        raise RuntimeError("TYPESAFE_API_KEY is not set")
    body = {
        "model": MODEL,
        "state": {"question": question},
        "questions": {"answer": {"type": "noul", "instructions": INSTRUCTIONS}},
    }
    req = urllib.request.Request(
        TYPESAFE_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "yes-or-no/0.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    p_yes = float(data["answers"]["answer"]["noul"])
    return {
        "question": question,
        "p_yes": p_yes,
        "answer": "yes" if p_yes >= 0.5 else "no",
        "model": data.get("model", MODEL),
        "usage": data.get("usage", {}),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj).encode(), "application/json")

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/ask":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            question = str(payload.get("question", "")).strip()
            if not question:
                self._json(400, {"error": "question is required"})
                return
            self._json(200, ask_jev(question))
        except urllib.error.HTTPError as e:
            self._json(502, {"error": f"Jev HTTP {e.code}: {e.read().decode(errors='replace')}"})
        except Exception as e:  # noqa: BLE001
            self._json(500, {"error": str(e)})

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    print(f"Yes or No -> http://localhost:{PORT}  (model={MODEL})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
