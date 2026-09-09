"""Generate an authenticated credential challenge for authorized solvers."""

from __future__ import annotations

import secrets

from api_keys import EXTERNAL_SERVICE_API_KEYS
from crypto_service import encrypt_json
from external_services import ExternalServiceConfigurationError, send_audit_event


def create_challenge(passphrase: str) -> tuple[dict[str, str], str]:
    """Create credentials and return them with their authenticated envelope."""
    credentials = {
        "username": f"user_{secrets.token_hex(6)}",
        "password": secrets.token_urlsafe(24),
    }
    envelope = encrypt_json(credentials, passphrase)
    return credentials, envelope.to_json()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate a secure credential challenge.")
    parser.add_argument("--audit-service", choices=EXTERNAL_SERVICE_API_KEYS)
    parser.add_argument("--audit-url", help="HTTPS endpoint for an optional audit event")
    args = parser.parse_args()
    if bool(args.audit_service) != bool(args.audit_url):
        parser.error("--audit-service and --audit-url must be supplied together.")

    passphrase = secrets.token_urlsafe(32)
    credentials, envelope = create_challenge(passphrase)
    if args.audit_service:
        try:
            status = send_audit_event(
                args.audit_service,
                args.audit_url,
                {"event": "challenge_created", "envelope_version": 2},
            )
        except (ExternalServiceConfigurationError, OSError) as exc:
            print(f"Audit event was not sent: {exc}")
            return 1
        print(f"Audit event sent ({status}).")
    print("=== Secure Authentication Challenge ===")
    print("Encrypted envelope:")
    print(envelope)
    print("\nFor this local demo only, give the authorized solver this passphrase:")
    print(passphrase)
    while True:
        username = input("Username: ")
        password = input("Password: ")
        if (username, password) == (credentials["username"], credentials["password"]):
            print("Authenticated!\nFLAG{authentication_successful}")
            return 0
        print("Invalid credentials.")


if __name__ == "__main__":
    raise SystemExit(main())
