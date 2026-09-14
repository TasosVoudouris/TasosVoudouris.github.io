"""Two-party additive-sharing Beaver multiplication demo."""
from __future__ import annotations
import secrets

P = 2**61 - 1


def share(x: int) -> tuple[int, int]:
    a = secrets.randbelow(P)
    return a, (x - a) % P


def add(x, y):
    return ((x[0] + y[0]) % P, (x[1] + y[1]) % P)


def sub(x, y):
    return ((x[0] - y[0]) % P, (x[1] - y[1]) % P)


def scale(c: int, x):
    return (c * x[0] % P, c * x[1] % P)


def add_public(x, c: int):
    # Public constant can be added to one designated share.
    return ((x[0] + c) % P, x[1])


def open_share(x) -> int:
    return (x[0] + x[1]) % P


def dealer_triple():
    a = secrets.randbelow(P)
    b = secrets.randbelow(P)
    c = a * b % P
    return share(a), share(b), share(c)


def multiply(x, y, triple):
    a, b, c = triple
    e = open_share(sub(x, a))
    f = open_share(sub(y, b))
    z = add(c, add(scale(e, b), scale(f, a)))
    return add_public(z, e * f % P)


def main():
    for _ in range(100):
        x0 = secrets.randbelow(P)
        y0 = secrets.randbelow(P)
        z = multiply(share(x0), share(y0), dealer_triple())
        assert open_share(z) == x0 * y0 % P
    print("PASS: 100 Beaver multiplications over two-party additive shares.")


if __name__ == '__main__':
    main()
