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
        "example": "sk-proj-LAB7xK2mQ9vR4pT8nW3cY6hJ1sF5dA0uE2iB9oN4gZ7kP3",
        "authentication": "bearer",
    },

    "github": {
        "environment_variable": "GITHUB_TOKEN",
        "example": "github_pat_LAB01H7K9M4Q2V8R5T3N6W1C0Y9F4D7S2A8B5E",
        "authentication": "bearer",
    },

    "google_maps": {
        "environment_variable": "GOOGLE_MAPS_API_KEY",
        "example": "AIzaSyLAB7K2mQ9vR4pT8nW3cY6hJ1sF5dA0uE",
        "authentication": "query",
    },

    "stripe": {
        "environment_variable": "STRIPE_API_KEY",
        "example": "sk_test_LAB4Q7mK2vN9pR5tW8xC3yH6jF1sD0aE2",
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
