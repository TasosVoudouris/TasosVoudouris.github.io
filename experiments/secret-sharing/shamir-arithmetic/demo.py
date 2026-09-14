"""Educational Shamir arithmetic and degree-growth demo.

This is not a distributed MPC protocol. The degree-reduction helper deliberately
reconstructs through a trusted dealer so the polynomial invariant is visible.
"""
from __future__ import annotations
from dataclasses import dataclass
from random import Random

P = 97
RNG = Random(20260914)


def inv(x: int) -> int:
    return pow(x % P, -1, P)


def eval_poly(coeffs: list[int], x: int) -> int:
    acc = 0
    for c in reversed(coeffs):
        acc = (acc * x + c) % P
    return acc


def interpolate_zero(points: list[tuple[int, int]]) -> int:
    total = 0
    for i, (xi, yi) in enumerate(points):
        num = den = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            num = (num * (-xj)) % P
            den = (den * (xi - xj)) % P
        total = (total + yi * num * inv(den)) % P
    return total


@dataclass
class Sharing:
    xs: list[int]
    ys: list[int]
    degree: int

    def reconstruct(self, count: int | None = None) -> int:
        need = self.degree + 1
        use = len(self.xs) if count is None else count
        if use < need:
            raise ValueError(f"degree {self.degree} needs at least {need} shares")
        return interpolate_zero(list(zip(self.xs[:use], self.ys[:use])))

    def __add__(self, other: "Sharing") -> "Sharing":
        assert self.xs == other.xs
        return Sharing(self.xs, [(a + b) % P for a, b in zip(self.ys, other.ys)], max(self.degree, other.degree))

    def __mul__(self, other: "Sharing") -> "Sharing":
        assert self.xs == other.xs
        return Sharing(self.xs, [(a * b) % P for a, b in zip(self.ys, other.ys)], self.degree + other.degree)


def share(secret: int, threshold: int, n: int) -> Sharing:
    if not (1 <= threshold <= n < P):
        raise ValueError("need 1 <= threshold <= n < field modulus")
    degree = threshold - 1
    coeffs = [secret % P] + [RNG.randrange(P) for _ in range(degree)]
    xs = list(range(1, n + 1))
    return Sharing(xs, [eval_poly(coeffs, x) for x in xs], degree)


def trusted_degree_reduce(product: Sharing, threshold: int) -> Sharing:
    """Reveal to a trusted dealer and re-share at the original threshold.

    This is intentionally NOT secure MPC. It demonstrates the invariant that a
    product sharing must be brought back from degree 2(t-1) to degree t-1.
    """
    secret = product.reconstruct()
    return share(secret, threshold, len(product.xs))


def main() -> None:
    threshold, n = 3, 5
    x = share(12, threshold, n)
    y = share(19, threshold, n)

    assert x.reconstruct(threshold) == 12
    assert y.reconstruct(threshold) == 19

    z_add = x + y
    assert z_add.degree == threshold - 1
    assert z_add.reconstruct(threshold) == (12 + 19) % P

    z_mul = x * y
    assert z_mul.degree == 2 * (threshold - 1)
    assert z_mul.reconstruct(n) == (12 * 19) % P

    try:
        z_mul.reconstruct(threshold)
    except ValueError:
        pass
    else:
        raise AssertionError("product sharing must not pretend to keep the old threshold")

    reduced = trusted_degree_reduce(z_mul, threshold)
    assert reduced.degree == threshold - 1
    assert reduced.reconstruct(threshold) == (12 * 19) % P

    print("PASS: linear operations preserve degree; multiplication grows degree; trusted resharing restores it.")


if __name__ == "__main__":
    main()
