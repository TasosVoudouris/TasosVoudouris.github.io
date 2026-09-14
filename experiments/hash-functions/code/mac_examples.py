"""Correct standard-library examples for HMAC generation and verification."""

from __future__ import annotations

import hashlib
import hmac


DOMAIN = b"CryptoCave/API-request/v1\x00"


def encode_request(method: str, path: str, body: bytes) -> bytes:
    """Create one unambiguous byte representation before authentication.

    Length prefixes prevent tuples such as (``ab``, ``c``) and (``a``, ``bc``)
    from sharing an encoding.  A real protocol must specify normalization for
    paths, headers, numbers and character encodings just as carefully.
    """

    method_bytes = method.upper().encode("ascii")
    path_bytes = path.encode("utf-8")
    fields = (method_bytes, path_bytes, body)
    return DOMAIN + b"".join(len(field).to_bytes(8, "big") + field for field in fields)


def tag_request(key: bytes, method: str, path: str, body: bytes) -> bytes:
    """Generate a full-length HMAC-SHA-256 tag."""

    if len(key) < 16:
        raise ValueError("demo policy requires at least a 128-bit random key")
    return hmac.digest(key, encode_request(method, path, body), "sha256")


def verify_request(key: bytes, method: str, path: str, body: bytes, tag: bytes) -> bool:
    """Verify with a constant-time comparison."""

    expected = tag_request(key, method, path, body)
    return hmac.compare_digest(expected, tag)


def unsafe_plain_hash(message: bytes) -> bytes:
    """A checksum, not a MAC: anyone can recompute it after changing data."""

    return hashlib.sha256(message).digest()


def main() -> None:
    key = bytes.fromhex("00112233445566778899aabbccddeeff" * 2)
    body = b'{"amount":100,"currency":"EUR"}'
    tag = tag_request(key, "POST", "/transfer", body)
    print(f"tag: {tag.hex()}")
    print(f"original accepted: {verify_request(key, 'POST', '/transfer', body, tag)}")
    print(f"modified accepted: {verify_request(key, 'POST', '/transfer', body + b' ', tag)}")


if __name__ == "__main__":
    main()
