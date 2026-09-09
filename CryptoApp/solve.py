"""Decrypt a Crypto Authentication Lab envelope after API-key authorization."""

from __future__ import annotations

import argparse
import hmac
import sys

from api_keys import TRAINING_API_KEYS
from crypto_service import DecryptionError, decrypt_json


def is_authorized(api_key: str) -> bool:
    """Check the local training API key without leaking comparison timing."""
    return hmac.compare_digest(api_key, TRAINING_API_KEYS["challenge_solver"])


def solve(envelope: str, passphrase: str, api_key: str) -> dict[str, str]:
    """Return validated credentials for an authorized caller."""
    if not is_authorized(api_key):
        raise PermissionError("Invalid solver API key.")
    payload = decrypt_json(envelope, passphrase)
    username, password = payload.get("username"), payload.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        raise DecryptionError("Payload does not contain string credentials.")
    return {"username": username, "password": password}


def main() -> int:
    parser = argparse.ArgumentParser(description="Decrypt an authorized AES-256-GCM challenge.")
    parser.add_argument("envelope", help="JSON envelope emitted by challenge.py")
    parser.add_argument("passphrase", help="Passphrase supplied by the challenge owner")
    parser.add_argument("--api-key", required=True, help="Local training solver API key")
    args = parser.parse_args()
    try:
        credentials = solve(args.envelope, args.passphrase, args.api_key)
    except (PermissionError, DecryptionError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Envelope decrypted and authenticated.")
    print(f"Username: {credentials['username']}")
    print(f"Password: {credentials['password']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
