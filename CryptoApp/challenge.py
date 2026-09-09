"""Generate an authenticated credential challenge for authorized solvers."""

from __future__ import annotations

import secrets

from crypto_service import encrypt_json


def create_challenge(passphrase: str) -> tuple[dict[str, str], str]:
    """Create credentials and return them with their authenticated envelope."""
    credentials = {
        "username": f"user_{secrets.token_hex(6)}",
        "password": secrets.token_urlsafe(24),
    }
    envelope = encrypt_json(credentials, passphrase)
    return credentials, envelope.to_json()


def main() -> None:
    passphrase = secrets.token_urlsafe(32)
    credentials, envelope = create_challenge(passphrase)
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
            return
        print("Invalid credentials.")


if __name__ == "__main__":
    main()
