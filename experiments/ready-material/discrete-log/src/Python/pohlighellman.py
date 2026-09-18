"""Dependency-free educational Pohlig-Hellman implementation.

The implementation targets multiplicative subgroups modulo a prime and mirrors
CryptoCave's worked example.  It is deliberately simple and intended for small
teaching inputs, not cryptographic-scale factorization or attacks.
"""

from math import gcd, prod


def factor_integer(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def order_of_elem(g: int, p: int) -> int:
    if gcd(g, p) != 1:
        raise ValueError("g must be invertible modulo p")

    # For prime p, ord(g) divides p-1. Reduce p-1 by its prime factors.
    order = p - 1
    for q in factor_integer(order):
        while order % q == 0 and pow(g, order // q, p) == 1:
            order //= q
    return order


def dlog_small(g: int, h: int, p: int, order: int) -> int | None:
    value = 1
    for x in range(order):
        if value == h % p:
            return x
        value = (value * g) % p
    return None


def pohlig_prime_power(g: int, h: int, p: int, q: int, e: int) -> int:
    """Solve a DLP when g has exact order q**e."""
    subgroup_order = q**e
    gamma = pow(g, q ** (e - 1), p)  # order q
    x = 0

    for j in range(e):
        gx = pow(g, x, p)
        residual = (h * pow(gx, -1, p)) % p
        c = pow(residual, q ** (e - 1 - j), p)

        digit = dlog_small(gamma, c, p, q)
        if digit is None:
            raise ValueError("prime-power digit DLP failed")

        x += digit * (q**j)

    x %= subgroup_order
    if pow(g, x, p) != h % p:
        raise ValueError("prime-power solution failed validation")
    return x


def crt(residues: list[int], moduli: list[int]) -> int:
    modulus = prod(moduli)
    x = 0
    for residue, m in zip(residues, moduli):
        M = modulus // m
        x += residue * M * pow(M, -1, m)
    return x % modulus


def pohlig_hellman(g: int, h: int, p: int, order: int | None = None) -> int:
    if order is None:
        order = order_of_elem(g, p)

    factors = factor_integer(order)
    residues: list[int] = []
    moduli: list[int] = []

    for q, e in factors.items():
        prime_power = q**e
        cofactor = order // prime_power

        g_i = pow(g, cofactor, p)
        h_i = pow(h, cofactor, p)

        x_i = pohlig_prime_power(g_i, h_i, p, q, e)
        residues.append(x_i)
        moduli.append(prime_power)

    x = crt(residues, moduli)
    if pow(g, x, p) != h % p:
        raise ValueError("recovered logarithm failed validation")
    return x


def main() -> None:
    # Same deterministic example used in the article.
    p = 337
    g = 10
    secret = 233
    h = pow(g, secret, p)
    order = order_of_elem(g, p)

    recovered = pohlig_hellman(g, h, p, order)

    print(f"order(g) = {order}")
    print(f"factorization = {factor_integer(order)}")
    print(f"h = {h}")
    print(f"recovered = {recovered}")
    print(f"verified = {pow(g, recovered, p) == h}")

    # Exhaustive regression over the tiny toy group.
    for x in range(order):
        hx = pow(g, x, p)
        assert pohlig_hellman(g, hx, p, order) == x

    print(f"all x=0..{order - 1}: PASS")


if __name__ == "__main__":
    main()
