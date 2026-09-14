"""Gaussian integer arithmetic Z[i] with Euclidean division and gcd."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class GaussianInteger:
    a: int
    b: int = 0

    def __add__(self, other: "GaussianInteger") -> "GaussianInteger":
        return GaussianInteger(self.a + other.a, self.b + other.b)

    def __sub__(self, other: "GaussianInteger") -> "GaussianInteger":
        return GaussianInteger(self.a - other.a, self.b - other.b)

    def __mul__(self, other: "GaussianInteger") -> "GaussianInteger":
        return GaussianInteger(
            self.a * other.a - self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def conjugate(self) -> "GaussianInteger":
        return GaussianInteger(self.a, -self.b)

    def norm(self) -> int:
        return self.a * self.a + self.b * self.b

    def divmod(self, other: "GaussianInteger") -> tuple["GaussianInteger", "GaussianInteger"]:
        if other.norm() == 0:
            raise ZeroDivisionError
        product = self * other.conjugate()
        n = other.norm()
        q = GaussianInteger(round(product.a / n), round(product.b / n))
        r = self - q * other
        assert r.norm() < n or r.norm() == 0
        return q, r

    def __repr__(self) -> str:
        sign = "+" if self.b >= 0 else "-"
        return f"{self.a} {sign} {abs(self.b)}i"


def gaussian_gcd(x: GaussianInteger, y: GaussianInteger) -> GaussianInteger:
    while y.norm() != 0:
        _, r = x.divmod(y)
        x, y = y, r
    return x


def _self_test() -> None:
    z = GaussianInteger(3, 4)
    assert z.norm() == 25
    assert z * z.conjugate() == GaussianInteger(25, 0)
    a = GaussianInteger(11, 7)
    b = GaussianInteger(3, 2)
    q, r = a.divmod(b)
    assert a == q * b + r
    assert r.norm() < b.norm()
    g = gaussian_gcd(GaussianInteger(5, 0), GaussianInteger(2, 1))
    assert g.norm() in {1, 5}


if __name__ == "__main__":
    _self_test()
    print("Gaussian-integer checks: PASS")
