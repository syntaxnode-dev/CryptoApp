"""Optional, safe integration point for external audit services."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from api_keys import EXTERNAL_SERVICE_API_KEYS, get_external_api_key, is_example_api_key


class ExternalServiceConfigurationError(ValueError):
    """Raised before a request if an integration has no real credential."""


def _add_query_key(url: str, api_key: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["key"] = api_key
    return urlunparse(parsed._replace(query=urlencode(query)))


def build_audit_request(service: str, url: str, event: dict[str, Any]) -> Request:
    """Build an authenticated JSON request without exposing a key in logs."""
    if service not in EXTERNAL_SERVICE_API_KEYS:
        raise ExternalServiceConfigurationError(f"Unsupported external service: {service}")
    if urlparse(url).scheme != "https":
        raise ExternalServiceConfigurationError("External audit URLs must use HTTPS.")
    api_key = get_external_api_key(service)
    if is_example_api_key(api_key):
        variable = EXTERNAL_SERVICE_API_KEYS[service]["environment_variable"]
        raise ExternalServiceConfigurationError(
            f"Set {variable} to a real credential before enabling this integration."
        )

    headers = {"Content-Type": "application/json", "User-Agent": "CryptoAuthLab/2"}
    if EXTERNAL_SERVICE_API_KEYS[service]["authentication"] == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"
    else:
        url = _add_query_key(url, api_key)
    body = json.dumps(event, sort_keys=True).encode("utf-8")
    return Request(url, data=body, headers=headers, method="POST")


def send_audit_event(service: str, url: str, event: dict[str, Any]) -> int:
    """Submit a non-sensitive audit event and return the HTTP status code."""
    request = build_audit_request(service, url, event)
    with urlopen(request, timeout=10) as response:
        return response.status
