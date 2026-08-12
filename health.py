"""Health endpoint service."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


SERVICE_NAME = "health-service"
SERVICE_VERSION = "1.0.0"
OWNER = "admin"


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks."""

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._handle_health()
        else:
            self._send_error(404, "Not Found")

    def _handle_health(self):
        # Check authorization – only the owner may perform this.
        caller = self._get_caller()
        if caller != OWNER:
            self._send_error(403, "Forbidden")
            return

        # Check dependency – reject without retry on failure.
        try:
            dep_status = self._check_dependency()
        except Exception:
            dep_status = False

        if not dep_status:
            self._send_error(503, "Dependency unavailable")
            return

        response = {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "healthy": True,
        }

        self._send_json(200, response)

    def _get_caller(self):
        """Extract the caller identity from the request."""
        # Read Authorization header; default to empty string if absent.
        auth = self.headers.get("Authorization", "")
        return auth.split(" ")[-1] if auth else ""

    def _check_dependency(self):
        """Check external dependency. Returns True if healthy."""
        # Simulated dependency check – in a real impl would hit another service.
        return True

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        body = json.dumps({"error": message})
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        body = json.dumps(data)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        """Suppress default request logging."""
        pass


def main():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    print(f"Health service {SERVICE_NAME} v{SERVICE_VERSION} listening on :8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
