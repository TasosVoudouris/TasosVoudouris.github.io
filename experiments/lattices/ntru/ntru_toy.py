"""Small NTRU-style correctness demo using cyclic polynomial arithmetic.

Educational only. Parameters are not secure.
"""
from random import Random

rng = Random(19)
N, p, q = 7, 3, 31


def cyc_mul(a, b, mod):
    out = [0] * N
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % N] = (out[(i + j) % N] + x * y) % mod
    return out


def mat_inv_mod(M, mod):
    n = len(M)
    A = [[x % mod for x in row] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(M)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if A[r][col] % mod), None)
        if pivot is None:
            raise ValueError("not invertible")
        A[col], A[pivot] = A[pivot], A[col]
        inv = pow(A[col][col], -1, mod)
        A[col] = [(inv * x) % mod for x in A[col]]
        for r in range(n):
            if r == col:
                continue
            f = A[r][col] % mod
            if f:
                A[r] = [(x - f * y) % mod for x, y in zip(A[r], A[col])]
    return [row[n:] for row in A]


def convolution_matrix(f, mod):
    # column j is f * x^j in Z_mod[x]/(x^N-1)
    return [[f[(i - j) % N] % mod for j in range(N)] for i in range(N)]


def poly_inv(f, mod):
    invM = mat_inv_mod(convolution_matrix(f, mod), mod)
    # solve M g = 1; first column of M^{-1}
    return [invM[i][0] % mod for i in range(N)]


def centered(poly, mod):
    return [((x + mod // 2) % mod) - mod // 2 for x in poly]


def sample_ternary(weight=2):
    while True:
        v = [0] * N
        idx = list(range(N))
        rng.shuffle(idx)
        for i in idx[:weight]:
            v[i] = 1
        for i in idx[weight:2 * weight]:
            v[i] = -1
        yield v


def keygen():
    # Search for a small f invertible modulo p and q.
    candidates = sample_ternary(2)
    for _ in range(1000):
        f = next(candidates)
        f[0] += 1
        try:
            fp_inv = poly_inv(f, p)
            fq_inv = poly_inv(f, q)
        except ValueError:
            continue
        g = next(sample_ternary(2))
        h = [(p * x) % q for x in cyc_mul(g, fq_inv, q)]
        return (f, fp_inv), h
    raise RuntimeError("failed to find invertible toy key")


def encrypt(m, h):
    r = next(sample_ternary(1))
    return [(x + y) % q for x, y in zip(cyc_mul(r, h, q), m)]


def decrypt(e, sk):
    f, fp_inv = sk
    a = centered(cyc_mul(f, e, q), q)
    a_mod_p = [x % p for x in a]
    return cyc_mul(fp_inv, a_mod_p, p)


if __name__ == "__main__":
    sk, h = keygen()
    m = [1, 0, 2, 0, 1, 0, 0]
    e = encrypt(m, h)
    recovered = decrypt(e, sk)
    assert recovered == [x % p for x in m], (m, recovered)
    print("message  =", m)
    print("recovered=", recovered)
