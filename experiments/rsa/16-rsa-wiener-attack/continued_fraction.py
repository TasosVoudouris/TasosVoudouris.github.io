"""
Continued-fraction utilities used by the Wiener RSA attack chapter.

The implementation is intentionally explicit so the Euclidean algorithm,
continued-fraction terms, and convergents remain visible.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


def continued_fraction(
    numerator: int,
    denominator: int,
) -> list[int]:
    """Return the finite simple continued fraction of numerator/denominator."""
    if denominator == 0:
        raise ZeroDivisionError("continued fraction denominator cannot be zero")

    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    terms: list[int] = []

    while denominator:
        quotient = numerator // denominator
        terms.append(quotient)

        numerator, denominator = (
            denominator,
            numerator - quotient * denominator,
        )

    return terms


def convergents(
    terms: Iterable[int],
) -> Iterator[tuple[int, int]]:
    """
    Yield (numerator, denominator) convergents.

    Recurrence:
        h_i = a_i h_{i-1} + h_{i-2}
        k_i = a_i k_{i-1} + k_{i-2}
    """
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0

    for a in terms:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2

        yield h, k

        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k
