"""
Wiener's continued-fraction attack against toy RSA keys with very small d.

Educational local arithmetic only.

Classical setup used here:
    N = p*q
    e*d - k*phi(N) = 1

The attack enumerates convergents k/d of e/N and validates each candidate by
reconstructing phi(N), then p+q, then the factorization polynomial.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt

from continued_fraction import continued_fraction, convergents


@dataclass(frozen=True)
class WienerResult:
    d: int
    k: int
    p: int
    q: int
    phi: int
    convergent_index: int


def validate_rsa_candidate(
    N: int,
    e: int,
    candidate_k: int,
    candidate_d: int,
) -> tuple[int, int, int] | None:
    """
    Validate a candidate (k,d) from a convergent of e/N.

    If valid, return:
        (p, q, phi)

    Otherwise return None.
    """
    if candidate_k <= 0 or candidate_d <= 0:
        return None

    ed_minus_1 = e * candidate_d - 1

    if ed_minus_1 % candidate_k != 0:
        return None

    phi = ed_minus_1 // candidate_k

    # phi(N) = N - (p+q) + 1
    S = N - phi + 1

    # p and q must be roots of x^2 - S*x + N = 0.
    discriminant = S * S - 4 * N

    if discriminant < 0:
        return None

    root = isqrt(discriminant)

    if root * root != discriminant:
        return None

    if (S + root) % 2 != 0:
        return None

    p = (S + root) // 2
    q = (S - root) // 2

    if p <= 1 or q <= 1:
        return None

    if p * q != N:
        return None

    if (p - 1) * (q - 1) != phi:
        return None

    return p, q, phi


def wiener_attack(
    N: int,
    e: int,
) -> WienerResult | None:
    """Try classical Wiener's attack on public key (N,e)."""
    terms = continued_fraction(e, N)

    for index, (candidate_k, candidate_d) in enumerate(
        convergents(terms)
    ):
        validated = validate_rsa_candidate(
            N,
            e,
            candidate_k,
            candidate_d,
        )

        if validated is None:
            continue

        p, q, phi = validated

        return WienerResult(
            d=candidate_d,
            k=candidate_k,
            p=max(p, q),
            q=min(p, q),
            phi=phi,
            convergent_index=index,
        )

    return None
