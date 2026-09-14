"""Gaussian reduction and the one-dimensional NTRU analogy from the Ross-course notes.

Dependency-free educational reconstruction. Parameters are intentionally tiny / toy.
"""
from math import gcd


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def norm2(v):
    return dot(v, v)


def nearest_integer_ratio(num: int, den: int) -> int:
    if den <= 0:
        raise ValueError("denominator must be positive")
    sign = -1 if num < 0 else 1
    num = abs(num)
    q, r = divmod(num, den)
    if 2 * r >= den:
        q += 1
    return sign * q


def gauss_reduce(b1, b2):
    """Gauss reduction for a rank-2 integer lattice."""
    b1 = list(map(int, b1))
    b2 = list(map(int, b2))
    for _ in range(1000):
        if norm2(b2) < norm2(b1):
            b1, b2 = b2, b1
        mu = nearest_integer_ratio(dot(b1, b2), norm2(b1))
        if mu == 0:
            return b1, b2
        b2 = [x - mu * y for x, y in zip(b2, b1)]
    raise RuntimeError("Gauss reduction did not terminate")


def classical_gaussian_example():
    # Directly reconstructs the small 2D worksheet example.
    b1, b2 = gauss_reduce([104, 62], [74, 23])
    assert norm2(b1) <= norm2(b2)
    return b1, b2


def integer_ntru_demo():
    """A 1-dimensional NTRU analogy: h = g/f mod q, c = r*h + m mod q."""
    q = 122_430_513_841
    f = 231_231
    g = 195_698
    m = 123_456
    r = 101_010

    assert gcd(f, q) == 1
    assert gcd(f, g) == 1

    h = (pow(f, -1, q) * g) % q
    c = (r * h + m) % q

    # Honest decryption, matching the old worksheet algebra.
    a = (f * c) % q
    recovered = (pow(f, -1, g) * a) % g
    assert recovered == m

    # Public lattice L = <(1,h),(0,q)> contains the short vector (f,g).
    rb1, rb2 = gauss_reduce([1, h], [0, q])
    candidates = [rb1, rb2]
    assert any(v == [f, g] or v == [-f, -g] for v in candidates)

    return {
        "q": q,
        "f": f,
        "g": g,
        "h": h,
        "ciphertext": c,
        "recovered": recovered,
        "reduced_basis": candidates,
    }


if __name__ == "__main__":
    b1, b2 = classical_gaussian_example()
    print("Gaussian reduction:", b1, b2)
    out = integer_ntru_demo()
    print("integer-NTRU public h:", out["h"])
    print("recovered message:", out["recovered"])
    print("reduced public basis:", out["reduced_basis"])
    print("PASS: Gaussian reduction exposes the short secret vector in the 2D toy.")
