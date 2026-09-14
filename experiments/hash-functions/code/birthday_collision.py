"""Small, safe demonstrations of generic attacks on truncated SHA-256.

These functions attack an intentionally tiny digest, not SHA-256 itself.  The
leftmost ``bits`` of SHA-256 are retained so that exhaustive experiments finish
quickly.  Do not use a truncated digest this small in a real system.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Collision:
    """Two distinct messages with the same truncated digest."""

    first: bytes
    second: bytes
    digest: int
    evaluations: int


def truncated_sha256(message: bytes, bits: int) -> int:
    """Return the leftmost ``bits`` of SHA-256 as an integer.

    Converting the full digest before shifting preserves leading zero bits.  A
    common but incorrect approach converts a hexadecimal digest to ``bin``;
    that drops leading zeroes and can create variable-length outputs.
    """

    if not 1 <= bits <= 256:
        raise ValueError("bits must be between 1 and 256")
    full = int.from_bytes(hashlib.sha256(message).digest(), "big")
    return full >> (256 - bits)


def collision_probability(draws: int, bits: int) -> float:
    """Exact birthday-collision probability for uniform sampling.

    The implementation accumulates logarithms to avoid underflow.  It is
    intended for teaching-sized experiments; use the approximation below for
    enormous domains.
    """

    if draws < 0:
        raise ValueError("draws cannot be negative")
    if bits < 1:
        raise ValueError("bits must be positive")
    domain = 1 << bits
    if draws > domain:
        return 1.0
    log_no_collision = sum(math.log1p(-i / domain) for i in range(draws))
    return -math.expm1(log_no_collision)


def birthday_approximation(draws: int, bits: int) -> float:
    """Approximate collision probability: 1-exp(-q(q-1)/(2N))."""

    if draws < 0 or bits < 1:
        raise ValueError("draws must be non-negative and bits positive")
    domain = 1 << bits
    return -math.expm1(-(draws * (draws - 1)) / (2 * domain))


def samples_for_probability(probability: float, bits: int) -> float:
    """Invert the birthday approximation for a desired probability."""

    if not 0 < probability < 1:
        raise ValueError("probability must lie strictly between 0 and 1")
    if bits < 1:
        raise ValueError("bits must be positive")
    return math.sqrt(2 * (1 << bits) * -math.log1p(-probability))


def find_collision(bits: int = 16, max_evaluations: int | None = None) -> Collision:
    """Find a collision by retaining every digest seen so far.

    Messages are deterministic counter encodings, making this lab reproducible.
    The table is what creates birthday complexity: about 2**(bits/2) hash
    evaluations and the same order of memory.  Comparing only isolated pairs
    would instead require about 2**bits evaluations.
    """

    if not 1 <= bits <= 24:
        raise ValueError("the teaching demo limits bits to 1..24")
    limit = max_evaluations if max_evaluations is not None else (1 << bits) + 1
    seen: dict[int, bytes] = {}
    for counter in range(limit):
        message = counter.to_bytes(8, "big")
        digest = truncated_sha256(message, bits)
        previous = seen.get(digest)
        if previous is not None and previous != message:
            return Collision(previous, message, digest, counter + 1)
        seen[digest] = message
    raise RuntimeError("no collision within max_evaluations")


def find_preimage(target: int, bits: int = 16, max_evaluations: int | None = None) -> tuple[bytes, int]:
    """Find a preimage for one fixed truncated digest by exhaustive search."""

    if not 1 <= bits <= 24:
        raise ValueError("the teaching demo limits bits to 1..24")
    if not 0 <= target < (1 << bits):
        raise ValueError("target is outside the digest range")
    limit = max_evaluations if max_evaluations is not None else 1 << (bits + 2)
    for counter in range(limit):
        candidate = counter.to_bytes(8, "big")
        if truncated_sha256(candidate, bits) == target:
            return candidate, counter + 1
    raise RuntimeError("no preimage within max_evaluations")


def main() -> None:
    bits = 16
    collision = find_collision(bits)
    print(f"{bits}-bit collision after {collision.evaluations} evaluations")
    print(f"m1 = {collision.first.hex()}")
    print(f"m2 = {collision.second.hex()}")
    print(f"digest = {collision.digest:0{(bits + 3) // 4}x}")
    q50 = samples_for_probability(0.5, bits)
    print(f"approximate samples for 50% probability: {q50:.1f}")


if __name__ == "__main__":
    main()
