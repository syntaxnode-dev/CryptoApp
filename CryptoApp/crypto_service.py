"""Authenticated encryption helpers for the Crypto Authentication Lab."""

from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass
from typing import Any

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes


VERSION = 2
ALGORITHM = "AES-256-GCM"
KDF = "scrypt"
SALT_LENGTH = 16
NONCE_LENGTH = 12
KEY_LENGTH = 32
ASSOCIATED_DATA = b"crypto-authentication-lab:v2"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


class DecryptionError(ValueError):
    """Raised when an encrypted envelope is malformed or fails verification."""


@dataclass(frozen=True)
class EncryptedEnvelope:
    version: int
    algorithm: str
    kdf: str
    salt: str
    nonce: str
    ciphertext: str
    tag: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, serialized: str) -> "EncryptedEnvelope":
        try:
            data = json.loads(serialized)
            envelope = cls(**data)
        except (TypeError, json.JSONDecodeError) as exc:
            raise DecryptionError("Envelope is not valid JSON.") from exc
        if envelope.version != VERSION or envelope.algorithm != ALGORITHM or envelope.kdf != KDF:
            raise DecryptionError("Envelope uses an unsupported cryptographic format.")
        return envelope


def _encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode(value: str, field: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (TypeError, ValueError) as exc:
        raise DecryptionError(f"Envelope field '{field}' is not valid Base64.") from exc


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive an AES-256 key with a memory-hard, salted KDF."""
    if not isinstance(passphrase, str) or not passphrase:
        raise ValueError("A non-empty passphrase is required.")
    return scrypt(passphrase.encode("utf-8"), salt, key_len=KEY_LENGTH, N=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)


def encrypt_json(payload: dict[str, Any], passphrase: str) -> EncryptedEnvelope:
    plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    salt = get_random_bytes(SALT_LENGTH)
    nonce = get_random_bytes(NONCE_LENGTH)
    cipher = AES.new(derive_key(passphrase, salt), AES.MODE_GCM, nonce=nonce)
    cipher.update(ASSOCIATED_DATA)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return EncryptedEnvelope(VERSION, ALGORITHM, KDF, _encode(salt), _encode(nonce), _encode(ciphertext), _encode(tag))


def decrypt_json(serialized_envelope: str, passphrase: str) -> dict[str, Any]:
    envelope = EncryptedEnvelope.from_json(serialized_envelope)
    salt = _decode(envelope.salt, "salt")
    nonce = _decode(envelope.nonce, "nonce")
    ciphertext = _decode(envelope.ciphertext, "ciphertext")
    tag = _decode(envelope.tag, "tag")
    if len(salt) != SALT_LENGTH or len(nonce) != NONCE_LENGTH or len(tag) != AES.block_size:
        raise DecryptionError("Envelope contains invalid field lengths.")
    try:
        cipher = AES.new(derive_key(passphrase, salt), AES.MODE_GCM, nonce=nonce)
        cipher.update(ASSOCIATED_DATA)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        payload = json.loads(plaintext.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DecryptionError("Unable to decrypt or authenticate the envelope.") from exc
    if not isinstance(payload, dict):
        raise DecryptionError("Decrypted payload must be a JSON object.")
    return payload

