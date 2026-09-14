"""Toy negacyclic Ring-LWE encryption of a binary polynomial.

Educational only. Not an implementation of ML-KEM or any standardized scheme.
"""
from random import Random

rng = Random(7)
N = 8
q = 257


def centered(x, mod=q):
    x %= mod
    return x - mod if x > mod // 2 else x


def add(a, b, mod=q):
    return [(x + y) % mod for x, y in zip(a, b)]


def neg(a, mod=q):
    return [(-x) % mod for x in a]


def mul(a, b, mod=q):
    out = [0] * N
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            k = i + j
            if k < N:
                out[k] += x * y
            else:
                out[k - N] -= x * y  # x^N = -1
    return [x % mod for x in out]


def small_poly():
    return [rng.choice((-1, 0, 1)) % q for _ in range(N)]


def uniform_poly():
    return [rng.randrange(q) for _ in range(N)]


def keygen():
    s = small_poly()
    e = small_poly()
    a = uniform_poly()
    b = add(neg(mul(a, s)), e)
    return s, (b, a)


def encrypt(message, pk):
    b, a = pk
    u, e1, e2 = small_poly(), small_poly(), small_poly()
    c0 = add(add(mul(b, u), e1), [(q // 2) * bit % q for bit in message])
    c1 = add(mul(a, u), e2)
    return c0, c1


def decrypt(ciphertext, s):
    c0, c1 = ciphertext
    v = add(c0, mul(c1, s))
    # coefficients near 0 encode 0; near q/2 encode 1
    return [1 if abs(abs(centered(x)) - q / 2) < q / 4 else 0 for x in v]


if __name__ == "__main__":
    message = [1, 0, 1, 1, 0, 0, 1, 0]
    sk, pk = keygen()
    ct = encrypt(message, pk)
    recovered = decrypt(ct, sk)
    assert recovered == message, (message, recovered)
    print("message  =", message)
    print("recovered=", recovered)
