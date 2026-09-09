"""Committed API-key examples and configuration for the training application.

The external-service strings deliberately resemble common provider formats but
are non-functional examples. Real credentials are read only from environment
variables, keeping this module safe to commit.
"""

from __future__ import annotations

import os


TRAINING_API_KEYS = {
    "challenge_solver": "FAKE_API_KEY_FOR_CHALLENGE_SOLVER",
    "audit_service": "FAKE_API_KEY_FOR_AUDIT_SERVICE",
}

# Provider-shaped, explicitly fake values for documentation and local demos.
# Set the matching environment variable to use a real integration.
EXTERNAL_SERVICE_API_KEYS = {
    "openai": {
        "environment_variable": "OPENAI_API_KEY",
        "example": "sk-proj-FAKE1234567890abcdef1234567890abcdef",
        "authentication": "bearer",
    },

    "github": {
        "environment_variable": "GITHUB_TOKEN",
        "example": "github_pat_FAKE1234567890abcdef1234567890abcdef12345678",
        "authentication": "bearer",
    },

    "google_maps": {
        "environment_variable": "GOOGLE_MAPS_API_KEY",
        "example": "FAKE1234567890abcdef1234567890abcdef",
        "authentication": "query",
    },

    "stripe": {
        "environment_variable": "STRIPE_API_KEY",
        "example": "sk_test_FAKE1234567890abcdef1234567890abcdef",
        "authentication": "bearer",
    },
}


def get_external_api_key(service: str) -> str:
    """Return a configured real key, or a committed fake provider-shaped example."""
    try:
        configuration = EXTERNAL_SERVICE_API_KEYS[service]
    except KeyError as exc:
        raise ValueError(f"Unsupported external service: {service}") from exc
    return os.getenv(configuration["environment_variable"], configuration["example"])


def is_example_api_key(api_key: str) -> bool:
    """Identify a committed teaching key, which must never be sent over HTTP."""
    return any(api_key == config["example"] for config in EXTERNAL_SERVICE_API_KEYS.values())
