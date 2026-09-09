"""Work-in-progress HTTP application for the Crypto Authentication Lab.

The crypto and solver flows are usable. External audit delivery is deliberately
not enabled yet: the application only validates and prepares its configuration.
"""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from api_keys import EXTERNAL_SERVICE_API_KEYS
from challenge import create_challenge
from external_services import ExternalServiceConfigurationError, build_audit_request
from solve import solve


class LabApplication:
    """Coordinates challenge creation, authorized solving, and audit setup."""

    def __init__(self, audit_service: str | None = None, audit_url: str | None = None):
        self.audit_service = audit_service
        self.audit_url = audit_url

    def status(self) -> dict[str, Any]:
        return {
            "application": "Crypto Authentication Lab",
            "crypto": {"status": "ready", "algorithm": "AES-256-GCM"},
            "solver": {"status": "ready", "authorization": "training API key"},
            "external_audit": {
                "status": "work_in_progress",
                "configured_service": self.audit_service,
                "delivery_enabled": False,
                "available_services": sorted(EXTERNAL_SERVICE_API_KEYS),
            },
        }

    def create_challenge(self) -> dict[str, Any]:
        import secrets

        passphrase = secrets.token_urlsafe(32)
        _, envelope = create_challenge(passphrase)
        audit = self._prepare_audit_event()
        return {
            "envelope": json.loads(envelope),
            "demo_passphrase": passphrase,
            "audit": audit,
        }

    def solve_challenge(self, body: dict[str, Any]) -> dict[str, str]:
        if not isinstance(body.get("passphrase"), str) or not isinstance(body.get("api_key"), str):
            raise ValueError("passphrase and api_key must be strings.")
        envelope = body.get("envelope")
        if isinstance(envelope, str):
            serialized_envelope = envelope
        elif isinstance(envelope, dict):
            serialized_envelope = json.dumps(envelope)
        else:
            raise ValueError("envelope must be a JSON object or a JSON string.")
        return solve(serialized_envelope, body["passphrase"], body["api_key"])

    def _prepare_audit_event(self) -> dict[str, str]:
        """Validate the external configuration without dispatching a request yet."""
        if not self.audit_service:
            return {"status": "not_configured", "message": "Work in progress"}
        try:
            build_audit_request(
                self.audit_service,
                self.audit_url or "",
                {"event": "challenge_created", "envelope_version": 2},
            )
        except ExternalServiceConfigurationError as exc:
            return {"status": "configuration_required", "message": str(exc)}
        return {"status": "prepared_not_sent", "message": "Work in progress"}


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    content_length = int(handler.headers.get("Content-Length", "0"))
    try:
        payload = json.loads(handler.rfile.read(content_length))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    return payload


def make_handler(application: LabApplication) -> type[BaseHTTPRequestHandler]:
    class LabRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - method required by BaseHTTPRequestHandler
            if urlparse(self.path).path == "/health":
                self._send_json(HTTPStatus.OK, application.status())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})

        def do_POST(self) -> None:  # noqa: N802 - method required by BaseHTTPRequestHandler
            path = urlparse(self.path).path
            try:
                if path == "/challenges":
                    self._send_json(HTTPStatus.CREATED, application.create_challenge())
                elif path == "/solve":
                    self._send_json(HTTPStatus.OK, application.solve_challenge(_read_json(self)))
                elif path == "/audit/send":
                    self._send_json(
                        HTTPStatus.NOT_IMPLEMENTED,
                        {"error": "External audit delivery is Work in progress."},
                    )
                else:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})
            except (PermissionError, ValueError) as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            response = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return LabRequestHandler


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Crypto Authentication Lab HTTP application.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--audit-service", choices=EXTERNAL_SERVICE_API_KEYS)
    parser.add_argument("--audit-url", help="HTTPS audit endpoint; dispatch remains Work in progress")
    args = parser.parse_args()
    if bool(args.audit_service) != bool(args.audit_url):
        parser.error("--audit-service and --audit-url must be supplied together.")

    application = LabApplication(args.audit_service, args.audit_url)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(application))
    print(f"Crypto Authentication Lab listening on http://{args.host}:{args.port}")
    print("External audit delivery: Work in progress")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
