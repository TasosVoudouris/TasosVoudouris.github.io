"""Reconstruct the Ross-course NTRU lattice and recover an equivalent short key with LLL.

The public key is the N=7, p=3, q=41 toy from the original Sage notebooks.
This is educational only and intentionally insecure.
"""
from fractions import Fraction

N = 7
Q = 41
H_COEFFS = [30, 26, 8, 38, 2, 40, 20]
TARGET_F = [-1, 0, 1, 1, -1, 0, 1]
TARGET_G = [0, -1, -1, 0, 1, 0, 1]


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def gram_schmidt(basis):
    ortho = []
    mu = [[Fraction(0) for _ in basis] for _ in basis]
    for i, b in enumerate(basis):
        v = [Fraction(x) for x in b]
        for j, q in enumerate(ortho):
            den = dot(q, q)
            mu[i][j] = Fraction(dot(b, q), den)
            v = [x - mu[i][j] * y for x, y in zip(v, q)]
        ortho.append(v)
    return ortho, mu


def nearest_integer(x: Fraction) -> int:
    if x >= 0:
        return (2 * x.numerator + x.denominator) // (2 * x.denominator)
    return -nearest_integer(-x)


def lll_reduce(basis, delta=Fraction(3, 4)):
    B = [list(map(int, row)) for row in basis]
    k = 1
    while k < len(B):
        ortho, mu = gram_schmidt(B)
        for j in range(k - 1, -1, -1):
            q = nearest_integer(mu[k][j])
            if q:
                B[k] = [x - q * y for x, y in zip(B[k], B[j])]
                ortho, mu = gram_schmidt(B)
        lhs = dot(ortho[k], ortho[k])
        rhs = (delta - mu[k][k - 1] ** 2) * dot(ortho[k - 1], ortho[k - 1])
        if lhs >= rhs:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)
    return B


def circulant(first_row):
    # Same convention printed by Sage matrix.circulant in the source notebook.
    return [first_row[-i:] + first_row[:-i] if i else first_row[:] for i in range(len(first_row))]


def ntru_lattice_basis():
    H = circulant(H_COEFFS)
    I = [[1 if i == j else 0 for j in range(N)] for i in range(N)]
    Z = [[0] * N for _ in range(N)]
    rows = []
    for i in range(N):
        rows.append(I[i] + H[i])
    for i in range(N):
        rows.append(Z[i] + [Q * x for x in I[i]])
    return rows


def mul_minus_x4(poly):
    out = [0] * N
    for i, a in enumerate(poly):
        out[(i + 4) % N] -= a
    return out


def equivalent_to_target(v):
    phi, gamma = v[:N], v[N:]
    return mul_minus_x4(phi) == TARGET_F and mul_minus_x4(gamma) == TARGET_G


def main():
    basis = ntru_lattice_basis()
    reduced = lll_reduce(basis)
    reduced = sorted(reduced, key=lambda v: dot(v, v))

    recovered = next((v for v in reduced if equivalent_to_target(v)), None)
    assert recovered is not None, "LLL did not expose the expected equivalent short key"

    phi, gamma = recovered[:N], recovered[N:]
    assert dot(recovered, recovered) == 9
    assert mul_minus_x4(phi) == TARGET_F
    assert mul_minus_x4(gamma) == TARGET_G

    print("short LLL vector:", recovered)
    print("phi coefficients:", phi)
    print("gamma coefficients:", gamma)
    print("after multiplication by -x^4 mod (x^7-1):")
    print("f =", mul_minus_x4(phi))
    print("g =", mul_minus_x4(gamma))
    print("PASS: LLL recovers an NTRU-equivalent short secret pair.")


if __name__ == "__main__":
    main()
