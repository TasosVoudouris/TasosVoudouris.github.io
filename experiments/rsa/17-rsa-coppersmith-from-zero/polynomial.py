"""
Tiny integer-polynomial helpers.

Representation:
    [a0, a1, ..., ad]
means:
    a0 + a1*x + ... + ad*x^d

Educational only; no symbolic-algebra dependency is used.
"""

from __future__ import annotations


def trim(poly: list[int]) -> list[int]:
    out = poly[:]

    while len(out) > 1 and out[-1] == 0:
        out.pop()

    return out


def add(a: list[int], b: list[int]) -> list[int]:
    size = max(len(a), len(b))
    out = [0] * size

    for i in range(size):
        out[i] = (
            (a[i] if i < len(a) else 0)
            +
            (b[i] if i < len(b) else 0)
        )

    return trim(out)


def neg(a: list[int]) -> list[int]:
    return [-v for v in a]


def sub(a: list[int], b: list[int]) -> list[int]:
    return add(a, neg(b))


def scale(a: list[int], scalar: int) -> list[int]:
    return trim([scalar * v for v in a])


def mul(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)

    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj

    return trim(out)


def power(a: list[int], exponent: int) -> list[int]:
    if exponent < 0:
        raise ValueError("polynomial exponent must be non-negative")

    result = [1]
    base = a[:]
    e = exponent

    while e:
        if e & 1:
            result = mul(result, base)

        base = mul(base, base)
        e >>= 1

    return result


def shift_x(a: list[int], amount: int) -> list[int]:
    if amount < 0:
        raise ValueError("shift amount must be non-negative")

    return ([0] * amount) + a


def evaluate(a: list[int], value: int) -> int:
    result = 0

    for coefficient in reversed(a):
        result = result * value + coefficient

    return result


def scale_variable(a: list[int], X: int) -> list[int]:
    """
    Coefficients of f(X*x).

    If:
        f(x) = sum a_i x^i
    then:
        f(X*x) = sum (a_i X^i) x^i.
    """
    return [
        coefficient * (X ** i)
        for i, coefficient in enumerate(a)
    ]


def pad(a: list[int], dimension: int) -> list[int]:
    if len(a) > dimension:
        raise ValueError("polynomial degree exceeds lattice dimension")

    return a + [0] * (dimension - len(a))


def pretty(a: list[int]) -> str:
    """Simple human-readable polynomial string."""
    parts: list[str] = []

    for degree in range(len(a) - 1, -1, -1):
        coefficient = a[degree]

        if coefficient == 0:
            continue

        if degree == 0:
            term = str(abs(coefficient))
        elif degree == 1:
            term = (
                "x"
                if abs(coefficient) == 1
                else f"{abs(coefficient)}*x"
            )
        else:
            term = (
                f"x^{degree}"
                if abs(coefficient) == 1
                else f"{abs(coefficient)}*x^{degree}"
            )

        if not parts:
            parts.append(
                f"-{term}" if coefficient < 0 else term
            )
        else:
            sign = "-" if coefficient < 0 else "+"
            parts.append(f" {sign} {term}")

    return "".join(parts) if parts else "0"
