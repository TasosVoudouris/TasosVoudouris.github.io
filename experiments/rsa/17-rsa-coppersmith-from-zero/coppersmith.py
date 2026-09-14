"""
Transparent univariate Coppersmith / Howgrave-Graham teaching construction.

Fixed conceptual family:

    g_{i,j}(x) = x^j * N^(m-i) * f(x)^i

for:
    0 <= i < m
    0 <= j < degree(f)

plus:

    x^j * f(x)^m
for:
    0 <= j < t

Every basis polynomial vanishes modulo N^m at a root of f modulo N.

The variable is scaled by X before coefficient vectors are built.
"""

from __future__ import annotations

from math import isqrt

from lll import lll_reduce
from polynomial import (
    evaluate,
    mul,
    pad,
    power,
    scale,
    scale_variable,
    shift_x,
)


def build_shift_polynomials(
    f: list[int],
    N: int,
    m: int,
    t: int,
) -> list[list[int]]:
    if m <= 0:
        raise ValueError("m must be positive")

    if t <= 0:
        raise ValueError("t must be positive")

    delta = len(f) - 1
    polynomials: list[list[int]] = []

    for i in range(m):
        f_power = power(f, i)
        modulus_power = N ** (m - i)

        for j in range(delta):
            g = shift_x(
                scale(f_power, modulus_power),
                j,
            )
            polynomials.append(g)

    f_to_m = power(f, m)

    for j in range(t):
        polynomials.append(
            shift_x(f_to_m, j)
        )

    return polynomials


def build_lattice_basis(
    f: list[int],
    N: int,
    X: int,
    m: int = 2,
    t: int = 1,
) -> tuple[list[list[int]], list[list[int]]]:
    shifts = build_shift_polynomials(
        f=f,
        N=N,
        m=m,
        t=t,
    )

    dimension = len(shifts)

    basis = [
        pad(
            scale_variable(g, X),
            dimension,
        )
        for g in shifts
    ]

    return shifts, basis


def unscale_vector_to_polynomial(
    vector: list[int],
    X: int,
) -> list[int]:
    coefficients: list[int] = []

    for degree, value in enumerate(vector):
        scale_factor = X ** degree

        if value % scale_factor != 0:
            raise ValueError(
                "reduced coefficient is not divisible by X^degree"
            )

        coefficients.append(
            value // scale_factor
        )

    return coefficients


def squared_norm(vector: list[int]) -> int:
    return sum(value * value for value in vector)


def recover_small_root(
    f: list[int],
    N: int,
    X: int,
    m: int = 2,
    t: int = 1,
):
    """
    Return a dictionary with the educational attack trace.

    Root extraction is deliberately transparent: after LLL constructs an
    integer polynomial h(x), search only the promised interval [-X, X] for
    common integer roots of h and modular roots of f.

    The important cryptanalytic step is the lattice construction that turns
    the modular root into an integer root of h.
    """
    shifts, basis = build_lattice_basis(
        f=f,
        N=N,
        X=X,
        m=m,
        t=t,
    )

    reduced, iterations = lll_reduce(basis)
    shortest = reduced[0]

    h = unscale_vector_to_polynomial(
        shortest,
        X,
    )

    roots: list[int] = []

    for candidate in range(-X, X + 1):
        if evaluate(h, candidate) != 0:
            continue

        if evaluate(f, candidate) % N != 0:
            continue

        roots.append(candidate)

    dimension = len(shortest)

    return {
        "shifts": shifts,
        "basis": basis,
        "reduced_basis": reduced,
        "shortest_vector": shortest,
        "h": h,
        "roots": roots,
        "lll_iterations": iterations,
        "dimension": dimension,
        "norm_squared": squared_norm(shortest),
        "threshold_squared_numerator": N ** (2 * m),
        "threshold_squared_denominator": dimension,
    }
