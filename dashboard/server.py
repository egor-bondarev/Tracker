"""Serve the homelab dashboard and its read-only Tracker check."""

import json
import os
import socket
from datetime import datetime
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


def read_snapshot(path):
    try:
        with path.open(encoding="utf-8-sig") as file:
            data = json.load(file)
        if datetime.fromisoformat(data["collected_at"]).utcoffset() is None:
            return {"state": "unavailable"}
    except (OSError, TypeError, KeyError, ValueError, OverflowError):
        return {"state": "unavailable"}
    return {"state": "available", "snapshot": data}


SOURCES = {
    "windows": Path("/metrics/windows/windows.json"),
    "wsl": Path("/metrics/wsl/wsl.json"),
    "docker": Path("/metrics/wsl/docker.json"),
}


def request_refresh(source):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(28)
        connection.connect("/metrics/control/refresh.sock")
        connection.sendall(source.encode("ascii") + b"\n")
        with connection.makefile("rb") as response:
            return response.readline(16) == b"ok\n"


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

    def send_json(self, payload, status=200):
        self.send_content(json.dumps(payload).encode("utf-8"), "application/json", status)

    def do_POST(self):
        prefix = "/api/metrics/"
        source = self.path[len(prefix):] if self.path.startswith(prefix) else ""
        if source not in SOURCES:
            self.send_json({"error": "Unknown metrics source"}, status=404)
            return
        if self.headers.get("X-Dashboard-Refresh") != "1":
            self.send_json({"error": "Refresh header required"}, status=403)
            return
        try:
            refreshed = request_refresh(source)
        except OSError:
            refreshed = False
        if not refreshed:
            self.send_json({"error": "Metrics refresh failed"}, status=503)
            return
        self.send_json(read_snapshot(SOURCES[source]))

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if self.path == "/api/metrics":
            self.send_json({name: read_snapshot(path) for name, path in SOURCES.items()})
            return

        if self.path == "/api/tracker/check":
            report = check_tracker(
                os.environ.get("TRACKER_WEB_URL", "http://host.docker.internal:8080"),
                os.environ.get("TRACKER_RECORD_URL", "http://host.docker.internal:8000"),
            )
            self.send_json(report)
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
