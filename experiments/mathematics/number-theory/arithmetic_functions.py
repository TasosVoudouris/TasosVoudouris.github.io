"""Small computational-number-theory helpers for arithmetic functions."""
from __future__ import annotations
from math import isqrt


def factorint(n: int) -> dict[int, int]:
    if n < 1:
        raise ValueError("n must be positive")
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def tau(n: int) -> int:
    result = 1
    for e in factorint(n).values():
        result *= e + 1
    return result


def sigma(n: int) -> int:
    result = 1
    for p, e in factorint(n).items():
        result *= (p ** (e + 1) - 1) // (p - 1)
    return result


def phi(n: int) -> int:
    result = n
    for p in factorint(n):
        result -= result // p
    return result


def mobius(n: int) -> int:
    fs = factorint(n)
    if any(e > 1 for e in fs.values()):
        return 0
    return -1 if len(fs) % 2 else 1


def dirichlet_convolution(f, g, n: int) -> int:
    total = 0
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            q = n // d
            total += f(d) * g(q)
            if d != q:
                total += f(q) * g(d)
    return total


def _self_test() -> None:
    assert factorint(360) == {2: 3, 3: 2, 5: 1}
    assert tau(100) == 9
    assert sigma(28) == 56
    assert phi(36) == 12
    assert mobius(30) == -1
    assert mobius(12) == 0
    one = lambda _: 1
    ident = lambda n: n
    assert dirichlet_convolution(one, ident, 12) == sigma(12)


if __name__ == "__main__":
    _self_test()
    print("arithmetic-function checks: PASS")
