"""Hash helpers shared by the reviewed CryptoSage demonstrations."""

import hashlib


def to_bytes(value):
    """Return an unambiguous byte representation for common demo inputs.

    Protocol implementations should define a schema for every encoded object.
    This helper is intentionally small and is suitable only for these examples.
    """

    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    return str(value).encode("utf-8")


def digest(message):
    """Map ``message`` to a non-negative integer using legacy SHA-1.

    SHA-1 is retained to preserve the mathematics of the supplied examples.
    New designs should normally select SHA-256 or a newer approved hash.
    """

    encoded = to_bytes(message)
    return Integer(hashlib.sha1(encoded).hexdigest(), 16)

