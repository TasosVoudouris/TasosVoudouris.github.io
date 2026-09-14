"""Toy packed secret sharing over a prime field.

K secrets are fixed at K secret points, T random masks at T randomness points,
and N party shares are evaluations at N disjoint share points.
"""
from __future__ import annotations

from dataclasses import dataclass
import secrets


def lagrange_eval(points_values: list[tuple[int, int]], x: int, q: int) -> int:
    xs = [a % q for a, _ in points_values]
    if len(xs) != len(set(xs)):
        raise ValueError("interpolation points must be distinct")

    total = 0
    for i, (xi, yi) in enumerate(points_values):
        num = 1
        den = 1
        for j, (xj, _) in enumerate(points_values):
            if i == j:
                continue
            num = (num * (x - xj)) % q
            den = (den * (xi - xj)) % q
        total = (total + yi * num * pow(den, -1, q)) % q
    return total


@dataclass
class PackedSharing:
    q: int
    n: int
    k: int
    t: int
    secret_points: list[int]
    randomness_points: list[int]
    share_points: list[int]
    shares: list[int | None]
    degree_bound: int

    @classmethod
    def share(
        cls,
        secrets_: list[int],
        *,
        n: int,
        t: int,
        q: int,
    ) -> "PackedSharing":
        k = len(secrets_)
        if k + t > n:
            raise ValueError("need k + t <= n")
        if n + k + t >= q:
            raise ValueError("field is too small for this simple point layout")

        secret_points = [(-i) % q for i in range(1, k + 1)]
        randomness_points = [(-i) % q for i in range(k + 1, k + t + 1)]
        share_points = list(range(1, n + 1))

        all_points = secret_points + randomness_points + share_points
        if len(all_points) != len(set(all_points)):
            raise ValueError("secret, randomness, and share points must be disjoint")

        constraints = list(zip(secret_points, [s % q for s in secrets_]))
        constraints += list(
            zip(randomness_points, [secrets.randbelow(q) for _ in range(t)])
        )

        shares = [lagrange_eval(constraints, x, q) for x in share_points]
        return cls(
            q=q,
            n=n,
            k=k,
            t=t,
            secret_points=secret_points,
            randomness_points=randomness_points,
            share_points=share_points,
            shares=shares,
            degree_bound=k + t - 1,
        )

    def reconstruct(self) -> list[int]:
        available = [
            (x, y)
            for x, y in zip(self.share_points, self.shares)
            if y is not None
        ]
        if len(available) < self.degree_bound + 1:
            raise ValueError("not enough shares for this polynomial degree")
        return [lagrange_eval(available, x, self.q) for x in self.secret_points]

    def _binary(self, other: "PackedSharing", op) -> "PackedSharing":
        if (
            self.q, self.n, self.k, self.t,
            self.secret_points, self.randomness_points, self.share_points
        ) != (
            other.q, other.n, other.k, other.t,
            other.secret_points, other.randomness_points, other.share_points
        ):
            raise ValueError("incompatible packed sharings")

        z = PackedSharing.__new__(PackedSharing)
        z.q, z.n, z.k, z.t = self.q, self.n, self.k, self.t
        z.secret_points = self.secret_points.copy()
        z.randomness_points = self.randomness_points.copy()
        z.share_points = self.share_points.copy()
        z.shares = [
            None if a is None or b is None else op(a, b) % self.q
            for a, b in zip(self.shares, other.shares)
        ]
        return z

    def __add__(self, other: "PackedSharing") -> "PackedSharing":
        z = self._binary(other, lambda a, b: a + b)
        z.degree_bound = max(self.degree_bound, other.degree_bound)
        return z

    def __mul__(self, other: "PackedSharing") -> "PackedSharing":
        z = self._binary(other, lambda a, b: a * b)
        z.degree_bound = self.degree_bound + other.degree_bound
        return z


if __name__ == "__main__":
    q, n, t = 101, 30, 10
    xs = [1, 2, 3, 4, 5]
    ys = [5, 9, 10, 11, 5]

    x = PackedSharing.share(xs, n=n, t=t, q=q)
    y = PackedSharing.share(ys, n=n, t=t, q=q)

    # Drop exactly the number allowed for base reconstruction.
    for i in range(n - (len(xs) + t)):
        x.shares[i] = None
    assert x.reconstruct() == xs

    # Addition preserves the original degree bound.
    xa = PackedSharing.share(xs, n=n, t=t, q=q)
    ya = PackedSharing.share(ys, n=n, t=t, q=q)
    z_add = xa + ya
    assert z_add.reconstruct() == [(a + b) % q for a, b in zip(xs, ys)]

    # Multiplication doubles the degree. With all 30 shares, degree 28 is recoverable.
    z_mul = xa * ya
    assert z_mul.degree_bound == 28
    assert z_mul.reconstruct() == [(a * b) % q for a, b in zip(xs, ys)]

    print("packed-sharing checks passed")
