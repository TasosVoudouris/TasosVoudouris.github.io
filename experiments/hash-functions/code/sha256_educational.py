"""Readable SHA-256 core plus the state-continuation hook used by the lab.

Use :mod:`hashlib` in production.  This implementation deliberately exposes
the chaining state so that Merkle--Damgard iteration and length extension can
be studied and tested.
"""

from __future__ import annotations

import struct
from collections.abc import Iterable


MASK32 = 0xFFFFFFFF
INITIAL_STATE = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)
ROUND_CONSTANTS = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
    0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
    0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC,
    0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7,
    0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
    0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3,
    0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5,
    0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
    0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)


def _rotr(word: int, count: int) -> int:
    return ((word >> count) | (word << (32 - count))) & MASK32


def _choose(x: int, y: int, z: int) -> int:
    return (x & y) ^ (~x & z)


def _majority(x: int, y: int, z: int) -> int:
    return (x & y) ^ (x & z) ^ (y & z)


def sha256_padding(message_length: int) -> bytes:
    """Return FIPS 180-4 padding for a byte-aligned message length."""

    if message_length < 0:
        raise ValueError("message_length cannot be negative")
    if message_length >= 1 << 61:
        raise ValueError("SHA-256 encodes a length smaller than 2**64 bits")
    zero_count = (56 - (message_length + 1) % 64) % 64
    return b"\x80" + b"\x00" * zero_count + struct.pack(">Q", message_length * 8)


def _schedule(block: bytes) -> list[int]:
    if len(block) != 64:
        raise ValueError("a SHA-256 block is exactly 64 bytes")
    words = list(struct.unpack(">16I", block)) + [0] * 48
    for index in range(16, 64):
        s0 = _rotr(words[index - 15], 7) ^ _rotr(words[index - 15], 18) ^ (words[index - 15] >> 3)
        s1 = _rotr(words[index - 2], 17) ^ _rotr(words[index - 2], 19) ^ (words[index - 2] >> 10)
        words[index] = (words[index - 16] + s0 + words[index - 7] + s1) & MASK32
    return words


def compress(state: Iterable[int], block: bytes) -> tuple[int, ...]:
    """Apply the SHA-256 compression function to one block."""

    chaining = tuple(state)
    if len(chaining) != 8 or any(not 0 <= word <= MASK32 for word in chaining):
        raise ValueError("state must contain eight 32-bit words")
    a, b, c, d, e, f, g, h = chaining
    for constant, word in zip(ROUND_CONSTANTS, _schedule(block)):
        upper1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
        temp1 = (h + upper1 + _choose(e, f, g) + constant + word) & MASK32
        upper0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
        temp2 = (upper0 + _majority(a, b, c)) & MASK32
        a, b, c, d, e, f, g, h = (
            (temp1 + temp2) & MASK32,
            a,
            b,
            c,
            (d + temp1) & MASK32,
            e,
            f,
            g,
        )
    return tuple((old + new) & MASK32 for old, new in zip(chaining, (a, b, c, d, e, f, g, h)))


def _process_blocks(data: bytes, state: Iterable[int]) -> tuple[int, ...]:
    if len(data) % 64:
        raise ValueError("data must contain complete SHA-256 blocks")
    result = tuple(state)
    for offset in range(0, len(data), 64):
        result = compress(result, data[offset : offset + 64])
    return result


def state_to_digest(state: Iterable[int]) -> bytes:
    words = tuple(state)
    if len(words) != 8:
        raise ValueError("state must contain eight words")
    return struct.pack(">8I", *words)


def digest_to_state(digest: bytes) -> tuple[int, ...]:
    if len(digest) != 32:
        raise ValueError("a SHA-256 digest is 32 bytes")
    return struct.unpack(">8I", digest)


def sha256(message: bytes) -> bytes:
    """Hash ``message`` from the standard initial value."""

    padded = message + sha256_padding(len(message))
    return state_to_digest(_process_blocks(padded, INITIAL_STATE))


def continue_from_digest(digest: bytes, suffix: bytes, processed_length: int) -> bytes:
    """Continue SHA-256 from a published chaining value.

    ``processed_length`` is the number of bytes already absorbed, including
    the original message's glue padding, and must therefore be block aligned.
    This interface exists solely to demonstrate length extension.
    """

    if processed_length < 0 or processed_length % 64:
        raise ValueError("processed_length must be a non-negative multiple of 64")
    final_blocks = suffix + sha256_padding(processed_length + len(suffix))
    state = _process_blocks(final_blocks, digest_to_state(digest))
    return state_to_digest(state)
