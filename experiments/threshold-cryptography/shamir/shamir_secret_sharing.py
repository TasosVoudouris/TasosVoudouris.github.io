"""From-scratch Shamir secret sharing over a prime field."""
from __future__ import annotations

import secrets
from typing import Iterable


def eval_poly(coeffs: list[int], x: int, q: int) -> int:
    acc = 0
    for coeff in reversed(coeffs):
        acc = (acc * x + coeff) % q
    return acc


def share(secret: int, *, threshold: int, n: int, q: int) -> list[tuple[int, int]]:
    if not (1 <= threshold <= n):
        raise ValueError("require 1 <= threshold <= n")
    if n >= q:
        raise ValueError("need at least n distinct nonzero field points")
    if not 0 <= secret < q:
        raise ValueError("secret must be represented in F_q")

    coeffs = [secret] + [secrets.randbelow(q) for _ in range(threshold - 1)]
    return [(x, eval_poly(coeffs, x, q)) for x in range(1, n + 1)]


def interpolate_at_zero(points: Iterable[tuple[int, int]], q: int) -> int:
    pts = list(points)
    xs = [x % q for x, _ in pts]
    if len(xs) != len(set(xs)):
        raise ValueError("x-coordinates must be distinct")

    secret = 0
    for i, (xi, yi) in enumerate(pts):
        num = 1
        den = 1
        for j, (xj, _) in enumerate(pts):
            if i == j:
                continue
            num = (num * (-xj)) % q
            den = (den * (xi - xj)) % q
        secret = (secret + yi * num * pow(den, -1, q)) % q
    return secret


if __name__ == "__main__":
    q = 2**127 - 1
    threshold, n = 3, 6
    secret = 123456789

    shares = share(secret, threshold=threshold, n=n, q=q)
    assert interpolate_at_zero(shares[:threshold], q) == secret
    assert interpolate_at_zero(shares[-threshold:], q) == secret

    print("shares:", shares)
    print("Shamir reconstruction checks passed")
