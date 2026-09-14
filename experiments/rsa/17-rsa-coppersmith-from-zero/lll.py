"""
Small exact LLL implementation for the Coppersmith teaching example.

This is deliberately simple:
- integer row basis;
- exact Fraction-based Gram-Schmidt;
- full recomputation after size-reduction operations;
- delta = 3/4 by default.

It is suitable for the tiny 7-dimensional demo, not for serious lattice work.
"""

from __future__ import annotations

from fractions import Fraction
from math import floor


Vector = list[int]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def gram_schmidt(
    basis: list[Vector],
):
    n = len(basis)
    dimension = len(basis[0])

    orthogonal = []
    mu = [
        [Fraction(0) for _ in range(n)]
        for _ in range(n)
    ]
    norms = [Fraction(0) for _ in range(n)]

    for i in range(n):
        source = [
            Fraction(value)
            for value in basis[i]
        ]
        v = source[:]

        for j in range(i):
            if norms[j] == 0:
                raise ValueError("basis vectors are linearly dependent")

            mu[i][j] = Fraction(
                dot(source, orthogonal[j]),
                norms[j],
            )

            for coordinate in range(dimension):
                v[coordinate] -= (
                    mu[i][j]
                    * orthogonal[j][coordinate]
                )

        orthogonal.append(v)
        norms[i] = dot(v, v)

    return orthogonal, mu, norms


def nearest_integer(value: Fraction) -> int:
    """
    Nearest integer using floor(x + 1/2).

    Tie convention is irrelevant for this deterministic teaching basis.
    """
    return floor(value + Fraction(1, 2))


def lll_reduce(
    basis: list[Vector],
    delta: Fraction = Fraction(3, 4),
) -> tuple[list[Vector], int]:
    if not basis:
        raise ValueError("basis cannot be empty")

    dimension = len(basis[0])

    if any(len(row) != dimension for row in basis):
        raise ValueError("all basis vectors need equal dimension")

    B = [
        [int(value) for value in row]
        for row in basis
    ]

    k = 1
    iterations = 0

    while k < len(B):
        iterations += 1

        if iterations > 100_000:
            raise RuntimeError("LLL iteration guard triggered")

        # Size reduction.
        for j in range(k - 1, -1, -1):
            _, mu, _ = gram_schmidt(B)
            q = nearest_integer(mu[k][j])

            if q != 0:
                B[k] = [
                    current - q * previous
                    for current, previous
                    in zip(B[k], B[j])
                ]

        # Lovasz condition.
        _, mu, norms = gram_schmidt(B)

        if norms[k] >= (
            delta - mu[k][k - 1] ** 2
        ) * norms[k - 1]:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)

    return B, iterations
