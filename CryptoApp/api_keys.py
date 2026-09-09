"""Committed API-key examples and configuration for the training application.

The external-service strings deliberately resemble common provider formats but
are non-functional examples. Real credentials are read only from environment
variables, keeping this module safe to commit.
"""

from __future__ import annotations

import os


TRAINING_API_KEYS = {
    "challenge_solver": "fake_api_key_training_solver_4a9c1e8b7d3f",
    "audit_service": "fake_api_key_training_audit_2f6d9a0c5b1e",
}

# Provider-shaped, explicitly fake values for documentation and local demos.
# Set the matching environment variable to use a real integration.
EXTERNAL_SERVICE_API_KEYS = {
    "openai": {
        "environment_variable": "OPENAI_API_KEY",
        "example": "sk-proj-FAKE_EXAMPLE_NOT_A_REAL_OPENAI_KEY",
    },
    "github": {
        "environment_variable": "GITHUB_TOKEN",
        "example": "github_pat_FAKE_EXAMPLE_NOT_A_REAL_GITHUB_TOKEN",
    },
    "google_maps": {
        "environment_variable": "GOOGLE_MAPS_API_KEY",
        "example": "AIzaFAKE_EXAMPLE_NOT_A_REAL_GOOGLE_KEY",
    },
    "stripe": {
        "environment_variable": "STRIPE_API_KEY",
        "example": "sk_test_FAKE_EXAMPLE_NOT_A_REAL_STRIPE_KEY",
    },
}


def get_external_api_key(service: str) -> str:
    """Return a configured real key, or a committed fake provider-shaped example."""
    try:
        configuration = EXTERNAL_SERVICE_API_KEYS[service]
    except KeyError as exc:
        raise ValueError(f"Unsupported external service: {service}") from exc
    return os.getenv(configuration["environment_variable"], configuration["example"])
