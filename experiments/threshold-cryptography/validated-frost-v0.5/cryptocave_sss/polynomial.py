"""Polynomial evaluation and interpolation over a prime field."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

if __package__:
    from .field import inverse, require_prime
else:
    from field import inverse, require_prime

Point = tuple[int, int]


def evaluate(coefficients: Sequence[int], point: int, modulus: int) -> int:
    """Evaluate a polynomial with Horner's rule.

    Coefficients are ordered from the constant term upwards.  Thus
    ``[1, 2, 3]`` represents ``1 + 2*x + 3*x^2``.
    """

    require_prime(modulus)
    result = 0
    for coefficient in reversed(coefficients):
        result = (coefficient + point * result) % modulus
    return result


def _normalise_points(points: Iterable[Point], modulus: int) -> list[Point]:
    normalised = [(x % modulus, y % modulus) for x, y in points]
    if not normalised:
        raise ValueError("at least one point is required")

    x_values = [x for x, _ in normalised]
    if len(set(x_values)) != len(x_values):
        raise ValueError("interpolation points must have distinct x-coordinates")
    return normalised


def lagrange_coefficients(
    x_values: Sequence[int], target: int, modulus: int
) -> list[int]:
    """Return the Lagrange coefficients for evaluation at ``target``."""

    require_prime(modulus)
    xs = [x % modulus for x in x_values]
    if not xs:
        raise ValueError("at least one x-coordinate is required")
    if len(set(xs)) != len(xs):
        raise ValueError("x-coordinates must be distinct")

    target %= modulus
    coefficients: list[int] = []
    for i, x_i in enumerate(xs):
        numerator = 1
        denominator = 1
        for j, x_j in enumerate(xs):
            if i == j:
                continue
            numerator = numerator * (target - x_j) % modulus
            denominator = denominator * (x_i - x_j) % modulus
        coefficients.append(numerator * inverse(denominator, modulus) % modulus)
    return coefficients


def interpolate(points: Iterable[Point], target: int, modulus: int) -> int:
    """Evaluate the unique low-degree interpolating polynomial at ``target``."""

    normalised = _normalise_points(points, modulus)
    xs = [x for x, _ in normalised]
    weights = lagrange_coefficients(xs, target, modulus)
    return sum(weight * y for weight, (_, y) in zip(weights, normalised)) % modulus


def interpolate_coefficients(points: Iterable[Point], modulus: int) -> list[int]:
    """Return coefficients of the unique interpolating polynomial.

    This direct implementation mirrors the mathematical Lagrange formula.  It
    is compact and easy to audit, which is more important than speed here.
    """

    normalised = _normalise_points(points, modulus)
    result = [0] * len(normalised)

    for i, (x_i, y_i) in enumerate(normalised):
        basis = [1]
        denominator = 1

        for j, (x_j, _) in enumerate(normalised):
            if i == j:
                continue

            # Multiply the current basis by (x - x_j).
            expanded = [0] * (len(basis) + 1)
            for degree, coefficient in enumerate(basis):
                expanded[degree] = (
                    expanded[degree] - x_j * coefficient
                ) % modulus
                expanded[degree + 1] = (
                    expanded[degree + 1] + coefficient
                ) % modulus
            basis = expanded
            denominator = denominator * (x_i - x_j) % modulus

        scale = y_i * inverse(denominator, modulus) % modulus
        for degree, coefficient in enumerate(basis):
            result[degree] = (result[degree] + scale * coefficient) % modulus

    # Remove zero leading coefficients without changing the zero polynomial.
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def matrix_rank(matrix: Sequence[Sequence[int]], modulus: int) -> int:
    """Compute matrix rank modulo ``modulus`` with Gaussian elimination."""

    require_prime(modulus)
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("all matrix rows must have the same length")

    work = [[entry % modulus for entry in row] for row in matrix]
    rank = 0

    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue

        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_inverse = inverse(work[rank][column], modulus)
        work[rank] = [entry * pivot_inverse % modulus for entry in work[rank]]

        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % modulus
                for left, right in zip(work[row], work[rank])
            ]

        rank += 1
        if rank == len(work):
            break
    return rank


def demo() -> None:
    """Evaluate and reconstruct one small polynomial."""

    modulus = 101
    coefficients = [1, 2, 3]
    points = [(x, evaluate(coefficients, x, modulus)) for x in (1, 2, 3)]
    print("Polynomial coefficients [constant first]:", coefficients)
    print("f(2):", evaluate(coefficients, 2, modulus))
    print("Three evaluation points:", points)
    print("Interpolated f(0):", interpolate(points, 0, modulus))


if __name__ == "__main__":
    demo()
