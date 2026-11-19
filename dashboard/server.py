"""Serve the homelab dashboard and its read-only Tracker check."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from scripts.check_tracker import check_tracker


STATIC = Path(__file__).parent / "static"
ASSETS = {
    "/": ("index.html", "text/html"),
    "/dashboard": ("index.html", "text/html"),
    "/dashboard.css": ("dashboard.css", "text/css"),
    "/dashboard.js": ("dashboard.js", "text/javascript"),
}


class DashboardHandler(BaseHTTPRequestHandler):
    def send_content(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if self.path == "/api/tracker/check":
            report = check_tracker(
                os.environ.get("TRACKER_WEB_URL", "http://host.docker.internal:8080"),
                os.environ.get("TRACKER_RECORD_URL", "http://host.docker.internal:8000"),
            )
            self.send_content(json.dumps(report).encode("utf-8"), "application/json")
            return

        asset = ASSETS.get(self.path)
        if not asset:
            self.send_content(b"Not found", "text/plain", status=404)
            return
        filename, content_type = asset
        self.send_content((STATIC / filename).read_bytes(), content_type)


if __name__ == "__main__":
    with ThreadingHTTPServer(("0.0.0.0", 8088), DashboardHandler) as server:
        server.serve_forever()
