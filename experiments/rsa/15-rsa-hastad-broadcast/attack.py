"""
Core arithmetic for the educational Håstad broadcast-attack chapter.

This module intentionally implements CRT and exact integer roots from scratch so
the attack mirrors the mathematical derivation.

Educational toy code only.
"""

from __future__ import annotations

from math import gcd, prod
from typing import Sequence


def check_pairwise_coprime(moduli: Sequence[int]) -> None:
    """Raise ValueError unless every pair of moduli is coprime."""
    if len(moduli) < 2:
        raise ValueError("need at least two moduli")

    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            g = gcd(moduli[i], moduli[j])

            if g != 1:
                raise ValueError(
                    "moduli are not pairwise coprime: "
                    f"gcd({moduli[i]}, {moduli[j]}) = {g}"
                )


def crt(
    residues: Sequence[int],
    moduli: Sequence[int],
) -> tuple[int, int]:
    """
    Construct the unique CRT representative C in [0, P).

    Returns:
        (C, P)
    where
        P = product(moduli).
    """
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have the same length")

    if not residues:
        raise ValueError("need at least one congruence")

    check_pairwise_coprime(moduli)

    P = prod(moduli)
    total = 0

    for residue, modulus in zip(residues, moduli):
        partial = P // modulus
        inverse = pow(partial, -1, modulus)

        total += residue * partial * inverse

    return total % P, P


def integer_nth_root(value: int, n: int) -> tuple[int, bool]:
    """
    Return (floor(value^(1/n)), exact).

    Uses integer-only binary search.  No floating point is used.
    """
    if value < 0:
        raise ValueError("value must be non-negative")

    if n <= 0:
        raise ValueError("root degree must be positive")

    if value in (0, 1):
        return value, True

    low = 0
    high = 1

    while pow(high, n) <= value:
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2
        candidate = pow(mid, n)

        if candidate <= value:
            low = mid
        else:
            high = mid

    return low, pow(low, n) == value


def hastad_broadcast_recover(
    ciphertexts: Sequence[int],
    moduli: Sequence[int],
    exponent: int,
) -> int:
    """
    Recover a common textbook RSA message in the simple broadcast setting.

    The caller supplies ciphertexts satisfying conceptually:

        c_i = m^e mod N_i

    for pairwise-coprime moduli.

    This simple routine succeeds only when CRT reconstructs the exact integer
    m^e in its canonical range, so the resulting integer root is exact.
    """
    if exponent <= 1:
        raise ValueError("exponent must be > 1")

    C, _ = crt(ciphertexts, moduli)
    root, exact = integer_nth_root(C, exponent)

    if not exact:
        raise ValueError(
            "CRT reconstruction is not an exact e-th power; "
            "the simple broadcast assumptions are insufficient"
        )

    # Defense-in-depth verification: the recovered root must reproduce every
    # supplied ciphertext.
    for c, n in zip(ciphertexts, moduli):
        if pow(root, exponent, n) != c % n:
            raise ValueError("candidate root does not reproduce ciphertexts")

    return root
