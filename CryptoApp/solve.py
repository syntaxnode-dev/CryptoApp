import argparse
import base64
import hashlib
import json
import sys

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


WORDS = [
    "dragon",
    "monkey",
    "shadow",
    "letmein",
    "football",
    "sunshine",
    "princess",
    "welcome",
    "password",
    "trustno1",
]


def derive_key(word: str) -> bytes:
    return hashlib.md5(word.encode("utf-8")).digest()


def try_candidate(ciphertext: bytes, word: str):
    cipher = AES.new(derive_key(word), AES.MODE_ECB)

    try:
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        decoded = plaintext.decode("utf-8")
        data = json.loads(decoded)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return None

    return word, username, password, decoded


def solve(ciphertext_b64: str):
    try:
        ciphertext = base64.b64decode(ciphertext_b64.strip(), validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Ciphertext is not valid Base64.") from exc

    if not ciphertext or len(ciphertext) % AES.block_size != 0:
        raise ValueError(
            "Decoded ciphertext length must be a non-zero multiple of 16 bytes."
        )

    for word in WORDS:
        result = try_candidate(ciphertext, word)
        if result is not None:
            return result

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Brute-force the Crypto Authentication Lab ciphertext."
    )
    parser.add_argument(
        "ciphertext",
        nargs="?",
        help="Base64 ciphertext. If omitted, the script prompts for it.",
    )
    args = parser.parse_args()

    ciphertext_b64 = args.ciphertext or input("Ciphertext: ").strip()

    try:
        result = solve(ciphertext_b64)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if result is None:
        print("No valid key word was found.", file=sys.stderr)
        return 1

    word, username, password, plaintext = result
    print("Ciphertext successfully decrypted.")
    print(f"Key word : {word}")
    print(f"Username : {username}")
    print(f"Password : {password}")
    print(f"Plaintext: {plaintext}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
