"""Toy Rabin oblivious transfer for educational use.

Small fixed primes are intentional: this demonstrates the algebra, not security.
"""
from math import gcd


def crt(a: int, p: int, b: int, q: int) -> int:
    n = p * q
    return (a * q * pow(q, -1, p) + b * p * pow(p, -1, q)) % n


def four_square_roots(x2: int, p: int, q: int) -> list[int]:
    # Toy helper assumes p,q == 3 mod 4.
    rp = pow(x2, (p + 1) // 4, p)
    rq = pow(x2, (q + 1) // 4, q)
    roots = {crt(sp * rp % p, p, sq * rq % q, q) for sp in (1, -1) for sq in (1, -1)}
    return sorted(roots)


def recover_factor(x: int, y: int, n: int) -> int | None:
    g = gcd((x - y) % n, n)
    return g if 1 < g < n else None
