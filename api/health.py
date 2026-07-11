from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import json

from api._triage_service import LIVE_SAMPLE_IDS, PROMPT_VERSION, live_configuration_status


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        checks = live_configuration_status()
        configured = all(checks.values())
        body = json.dumps(
            {
                "status": "ok" if configured else "configuration_required",
                "service": "support-triage",
                "prompt_version": PROMPT_VERSION,
                "live_sample_ids": list(LIVE_SAMPLE_IDS),
                **checks,
            }
        ).encode("utf-8")
        self.send_response(200 if configured else 503)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return
