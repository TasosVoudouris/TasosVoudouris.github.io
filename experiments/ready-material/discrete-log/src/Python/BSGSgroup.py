"""Educational Baby-Step Giant-Step implementation for multiplicative DLPs.

This companion script is dependency-free and mirrors the CryptoCave article.
It is intended for small/teaching examples, not cryptographic-scale attacks.
"""

from math import gcd, isqrt


def ceil_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    m = isqrt(n)
    return m if m * m == n else m + 1


def order_of_elem(g: int, p: int) -> int:
    """Return the multiplicative order of g modulo p by direct search.

    This is deliberately simple and appropriate only for small examples.
    """
    if gcd(g, p) != 1:
        raise ValueError("g must be invertible modulo p")

    value = 1
    for order in range(1, p + 1):
        value = (value * g) % p
        if value == 1:
            return order

    raise RuntimeError("multiplicative order not found")


def bsgs(g: int, h: int, p: int, order: int | None = None) -> int | None:
    """Solve g^x = h (mod p) for the canonical x in [0, order-1]."""
    if order is None:
        order = order_of_elem(g, p)

    m = ceil_sqrt(order)

    baby: dict[int, int] = {}
    value = 1
    for j in range(m):
        baby.setdefault(value, j)
        value = (value * g) % p

    g_m = pow(g, m, p)
    factor = pow(g_m, -1, p)
    gamma = h % p

    for i in range(m):
        if gamma in baby:
            x = i * m + baby[gamma]
            if x < order and pow(g, x, p) == h % p:
                return x
        gamma = (gamma * factor) % p

    return None


def main() -> None:
    p = 17389
    g = 2
    h = 13896

    order = order_of_elem(g, p)
    x = bsgs(g, h, p, order)

    print(f"order(g) = {order}")
    print(f"x = {x}")
    print(f"verified = {x is not None and pow(g, x, p) == h}")


if __name__ == "__main__":
    main()
