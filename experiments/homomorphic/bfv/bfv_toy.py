"""Tiny BFV-style demo with addition and raw 3-component multiplication.

This is pedagogical code, not production BFV and not a parameterized HE library.
"""
from random import Random

rng = Random(23)
N, t, q = 4, 2, 65537
DELTA = q // t


def center(x):
    x %= q
    return x - q if x > q // 2 else x


def poly_add(a, b):
    return [(x + y) % q for x, y in zip(a, b)]


def poly_mul(a, b):
    out = [0] * N
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            k = i + j
            if k < N:
                out[k] += x * y
            else:
                out[k - N] -= x * y
    return [x % q for x in out]


def small():
    return [rng.choice((-1, 0, 1)) % q for _ in range(N)]


def uniform():
    return [rng.randrange(q) for _ in range(N)]


def keygen():
    s, a, e = small(), uniform(), small()
    b = [(-x + y) % q for x, y in zip(poly_mul(a, s), e)]
    return s, (b, a)


def encrypt(m, pk):
    b, a = pk
    u, e1, e2 = small(), small(), small()
    c0 = poly_add(poly_add(poly_mul(b, u), e1), [(DELTA * x) % q for x in m])
    c1 = poly_add(poly_mul(a, u), e2)
    return [c0, c1]


def decrypt_components(c, s):
    # Evaluate c_0 + c_1 s + c_2 s^2 + ...
    accum = [0] * N
    s_power = [1, 0, 0, 0]
    for component in c:
        accum = poly_add(accum, poly_mul(component, s_power))
        s_power = poly_mul(s_power, s)
    return [int(round(t * center(x) / q)) % t for x in accum]


def add_ct(c, d):
    return [poly_add(x, y) for x, y in zip(c, d)]


def mul_shape_only(c, d):
    """Return the raw three-component product shape.

    A complete BFV multiply must also perform the scheme-specific scale-down and,
    normally, relinearization. We intentionally do not fake those steps here.
    """
    raw = [[0] * N for _ in range(len(c) + len(d) - 1)]
    for i, ci in enumerate(c):
        for j, dj in enumerate(d):
            raw[i + j] = poly_add(raw[i + j], poly_mul(ci, dj))
    return raw


if __name__ == "__main__":
    sk, pk = keygen()
    m1, m2 = [1, 0, 1, 0], [1, 1, 0, 0]
    c1, c2 = encrypt(m1, pk), encrypt(m2, pk)
    assert decrypt_components(c1, sk) == m1
    assert decrypt_components(c2, sk) == m2

    c_add = add_ct(c1, c2)
    expected_add = [(x + y) % t for x, y in zip(m1, m2)]
    assert decrypt_components(c_add, sk) == expected_add

    raw_mul = mul_shape_only(c1, c2)
    assert len(raw_mul) == 3

    print("addition ok:", expected_add)
    print("raw multiplication ciphertext components:", len(raw_mul))
    print("note: scale-down/relinearization intentionally omitted")
