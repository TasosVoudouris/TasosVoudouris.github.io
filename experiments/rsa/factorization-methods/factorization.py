"""Educational RSA-factorization methods for structured toy moduli."""
from __future__ import annotations
from math import gcd, isqrt


def fermat_factor(n: int):
    if n % 2 == 0:
        return 2, n // 2
    a = isqrt(n)
    if a * a < n:
        a += 1
    while True:
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            p, q = a - b, a + b
            return min(p, q), max(p, q)
        a += 1


def pollard_p_minus_1(n: int, bound: int = 10000, base: int = 2):
    """Stage-1 Pollard p-1: succeeds when p-1 is sufficiently B-smooth."""
    a = base % n
    for j in range(2, bound + 1):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return min(d, n // d), max(d, n // d)
        if d == n:
            return None
    return None


def demo():
    # Close primes: Fermat is ideal.
    p, q = 1000003, 1000033
    assert fermat_factor(p * q) == (p, q)

    # 257-1 = 2^8 is very smooth, so Pollard p-1 succeeds quickly.
    p2, q2 = 257, 1009
    factors = pollard_p_minus_1(p2 * q2, bound=64)
    assert factors == (p2, q2)
    print("Fermat and Pollard p-1 toy checks passed")


if __name__ == "__main__":
    demo()
