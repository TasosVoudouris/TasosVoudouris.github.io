"""Small educational prime-field implementation.

This module intentionally models only F_p for prime p.  It checks primality
at construction time so division cannot silently pretend Z/nZ is a field.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isqrt


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True


def egcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_s, old_t, old_r


class PrimeField:
    def __init__(self, p: int):
        if not is_prime(p):
            raise ValueError("p must be prime to construct F_p")
        self.p = p

    def __call__(self, value: int) -> "Fp":
        return Fp(value % self.p, self)


@dataclass(frozen=True)
class Fp:
    value: int
    field: PrimeField

    def _coerce(self, other: int | "Fp") -> "Fp":
        if isinstance(other, Fp):
            if other.field.p != self.field.p:
                raise TypeError("cannot mix elements from different fields")
            return other
        return self.field(other)

    def __add__(self, other: int | "Fp") -> "Fp":
        other = self._coerce(other)
        return self.field(self.value + other.value)

    def __sub__(self, other: int | "Fp") -> "Fp":
        other = self._coerce(other)
        return self.field(self.value - other.value)

    def __mul__(self, other: int | "Fp") -> "Fp":
        other = self._coerce(other)
        return self.field(self.value * other.value)

    def __neg__(self) -> "Fp":
        return self.field(-self.value)

    def inverse(self) -> "Fp":
        if self.value == 0:
            raise ZeroDivisionError("0 has no multiplicative inverse")
        x, _, g = egcd(self.value, self.field.p)
        if g != 1:
            raise ZeroDivisionError("element is not invertible")
        return self.field(x)

    def __truediv__(self, other: int | "Fp") -> "Fp":
        return self * self._coerce(other).inverse()

    def __pow__(self, exponent: int) -> "Fp":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        return self.field(pow(self.value, exponent, self.field.p))

    def __repr__(self) -> str:
        return f"{self.value} (mod {self.field.p})"


def _self_test() -> None:
    F = PrimeField(23)
    a = F(7)
    assert a.inverse() == F(10)
    assert a * a.inverse() == F(1)
    assert F(3) + F(22) == F(2)
    assert F(5) ** 22 == F(1)
    try:
        PrimeField(15)
    except ValueError:
        pass
    else:
        raise AssertionError("composite modulus accepted as a field")


if __name__ == "__main__":
    _self_test()
    print("prime-field checks: PASS")
