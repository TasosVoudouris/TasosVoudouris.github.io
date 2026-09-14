"""End-to-end SHA-256 secret-prefix-MAC length-extension demonstration."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from sha256_educational import continue_from_digest, sha256_padding


@dataclass(frozen=True)
class Forgery:
    guessed_secret_length: int
    message: bytes
    tag: bytes


def forge_sha256_secret_prefix_mac(
    original: bytes,
    known_tag: bytes,
    suffix: bytes,
    guessed_secret_length: int,
) -> Forgery:
    """Forge ``SHA256(secret || message)`` for one secret-length guess."""

    if guessed_secret_length < 0:
        raise ValueError("guessed_secret_length cannot be negative")
    hidden_and_known_length = guessed_secret_length + len(original)
    glue_padding = sha256_padding(hidden_and_known_length)
    processed_length = hidden_and_known_length + len(glue_padding)
    forged_tag = continue_from_digest(known_tag, suffix, processed_length)
    return Forgery(
        guessed_secret_length,
        original + glue_padding + suffix,
        forged_tag,
    )


def main() -> None:
    # The attacker knows only original and published_tag.  The local secret and
    # verifier stand in for a vulnerable server.
    server_secret = b"server-side-key"
    original = b"comment=hello&role=user"
    suffix = b"&role=admin"
    published_tag = hashlib.sha256(server_secret + original).digest()

    accepted: Forgery | None = None
    for guess in range(8, 33):
        candidate = forge_sha256_secret_prefix_mac(original, published_tag, suffix, guess)
        expected = hashlib.sha256(server_secret + candidate.message).digest()
        if hmac.compare_digest(candidate.tag, expected):
            accepted = candidate
            break

    assert accepted is not None
    print(f"accepted secret-length guess: {accepted.guessed_secret_length}")
    print(f"forged message (hex): {accepted.message.hex()}")
    print(f"forged tag: {accepted.tag.hex()}")

    # HMAC does not expose a chaining value that can be resumed this way.
    real_hmac = hmac.digest(server_secret, accepted.message, "sha256")
    print(f"same forged tag accepted as HMAC: {hmac.compare_digest(accepted.tag, real_hmac)}")


if __name__ == "__main__":
    main()
